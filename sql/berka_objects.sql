-- =====================================================================
-- Berka - Third delivery: database objects
-- Run AFTER loading berka.sql (it does not modify berka.sql or its tables'
-- columns; it only adds new objects on top of the existing schema).
--
-- Contents
--   1. Supporting table : client_audit      (filled by a trigger)
--   2. Supporting index : idx_trans_account_date (speeds up balance lookups)
--   3. Function         : fn_account_balance
--   4. Procedure        : sp_account_statement
--   5. Trigger 1        : trg_trans_before_insert
--   6. Trigger 2        : trg_client_after_update
--   7. View             : vw_account_overview
--   8. Test queries
--
-- Works in MySQL 8.x (Workbench or mysql console).
-- =====================================================================

USE berka;

-- ---------------------------------------------------------------------
-- 1. Audit table (new table, used by trg_client_after_update)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS client_audit;
CREATE TABLE client_audit (
    audit_id          INT          NOT NULL AUTO_INCREMENT,
    client_id         BIGINT       NOT NULL,
    old_birth_number  BIGINT       NULL,
    new_birth_number  BIGINT       NULL,
    old_district_id   BIGINT       NULL,
    new_district_id   BIGINT       NULL,
    changed_by        VARCHAR(100) NOT NULL,
    changed_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (audit_id)
);

-- ---------------------------------------------------------------------
-- 2. Index on trans(account_id, date)
--    berka.sql only indexes trans_id; without this index every balance
--    lookup scans the 1,056,320 transactions.
--    (If you run the script twice, ignore the "Duplicate key name" error
--    or drop the index first.)
-- ---------------------------------------------------------------------
CREATE INDEX idx_trans_account_date ON trans (account_id, `date`, trans_id);

DELIMITER $$

-- ---------------------------------------------------------------------
-- 3. FUNCTION fn_account_balance(account_id, date)
--    Returns the balance of an account at a given date (balance of the
--    last transaction on or before that date). NULL date = current
--    balance. Returns 0 if the account has no transactions yet.
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_account_balance $$
CREATE FUNCTION fn_account_balance(p_account_id BIGINT, p_date DATE)
RETURNS DOUBLE
READS SQL DATA
BEGIN
    DECLARE v_balance DOUBLE;

    SET v_balance = (
        SELECT balance
        FROM trans
        WHERE account_id = p_account_id
          AND (p_date IS NULL OR `date` <= p_date)
        ORDER BY `date` DESC, trans_id DESC
        LIMIT 1
    );

    RETURN IFNULL(v_balance, 0);
END $$

-- ---------------------------------------------------------------------
-- 4. PROCEDURE sp_account_statement(account_id, from, to)
--    Bank statement of an account for a period.
--    Result set 1: summary (opening balance, total in, total out,
--                  number of transactions, closing balance)
--    Result set 2: detail of the transactions in the period
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_account_statement $$
CREATE PROCEDURE sp_account_statement(IN p_account_id BIGINT,
                                      IN p_from DATE,
                                      IN p_to DATE)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM account WHERE account_id = p_account_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account does not exist';
    END IF;

    IF p_from IS NULL OR p_to IS NULL OR p_from > p_to THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid date range (from must be <= to)';
    END IF;

    -- 1) Summary
    SELECT a.account_id,
           d.A2                                                          AS branch_district,
           a.frequency,
           p_from                                                        AS date_from,
           p_to                                                          AS date_to,
           ROUND(fn_account_balance(p_account_id, DATE_SUB(p_from, INTERVAL 1 DAY)), 2) AS opening_balance,
           ROUND(COALESCE(SUM(CASE WHEN t.type = 'PRIJEM'  THEN t.amount END), 0), 2)   AS total_in,
           ROUND(COALESCE(SUM(CASE WHEN t.type <> 'PRIJEM' THEN t.amount END), 0), 2)   AS total_out,
           COUNT(t.trans_id)                                             AS num_transactions,
           ROUND(fn_account_balance(p_account_id, p_to), 2)              AS closing_balance
    FROM account a
    JOIN district d ON d.A1 = a.district_id
    LEFT JOIN trans t
           ON t.account_id = a.account_id
          AND t.`date` BETWEEN p_from AND p_to
    WHERE a.account_id = p_account_id
    GROUP BY a.account_id, d.A2, a.frequency;

    -- 2) Detail
    SELECT trans_id, `date`, type, operation, k_symbol, amount, balance, bank, `account`
    FROM trans
    WHERE account_id = p_account_id
      AND `date` BETWEEN p_from AND p_to
    ORDER BY `date`, trans_id;
END $$

-- ---------------------------------------------------------------------
-- 5. TRIGGER 1: trg_trans_before_insert  (BEFORE INSERT ON trans)
--    - Rejects amounts <= 0 and invalid transaction types
--    - Rejects transactions for accounts that do not exist
--      (berka.sql has no foreign keys, so the trigger enforces it)
--    - Uses today's date if none is given
--    - Rejects dates before the account was opened
--    - Assigns trans_id automatically if none is given
--    - Calculates the resulting balance if none is given
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_trans_before_insert $$
CREATE TRIGGER trg_trans_before_insert
BEFORE INSERT ON trans
FOR EACH ROW
BEGIN
    DECLARE v_opened DATE;

    IF NEW.amount IS NULL OR NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction amount must be greater than 0';
    END IF;

    IF NEW.type NOT IN ('PRIJEM', 'VYDAJ', 'VYBER') OR NEW.type IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction type must be PRIJEM, VYDAJ or VYBER';
    END IF;

    SELECT `date` INTO v_opened FROM account WHERE account_id = NEW.account_id;
    IF v_opened IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account does not exist';
    END IF;

    IF NEW.`date` IS NULL THEN
        SET NEW.`date` = CURDATE();
    END IF;

    IF NEW.`date` < v_opened THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction date is before the account opening date';
    END IF;

    IF NEW.trans_id IS NULL THEN
        SET NEW.trans_id = (SELECT IFNULL(MAX(trans_id), 0) + 1 FROM trans);
    END IF;

    IF NEW.balance IS NULL THEN
        SET NEW.balance = fn_account_balance(NEW.account_id, NEW.`date`)
                          + IF(NEW.type = 'PRIJEM', NEW.amount, -NEW.amount);
    END IF;
END $$

-- ---------------------------------------------------------------------
-- 6. TRIGGER 2: trg_client_after_update  (AFTER UPDATE ON client)
--    Audit: stores old and new values in client_audit, with the MySQL
--    user and timestamp, only when something actually changed.
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_client_after_update $$
CREATE TRIGGER trg_client_after_update
AFTER UPDATE ON client
FOR EACH ROW
BEGIN
    IF NOT (OLD.birth_number <=> NEW.birth_number)
       OR NOT (OLD.district_id <=> NEW.district_id) THEN
        INSERT INTO client_audit (client_id,
                                  old_birth_number, new_birth_number,
                                  old_district_id,  new_district_id,
                                  changed_by)
        VALUES (NEW.client_id,
                OLD.birth_number, NEW.birth_number,
                OLD.district_id,  NEW.district_id,
                CURRENT_USER());
    END IF;
END $$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 7. VIEW vw_account_overview
--    One row per account with its owner, the owner's decoded birth date
--    and gender (from birth_number: month > 50 = female), branch district,
--    loan, card and current balance.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_account_overview AS
SELECT a.account_id,
       a.`date`                                             AS opened_on,
       a.frequency                                          AS statement_frequency,
       d.A2                                                 AS branch_district,
       d.A3                                                 AS region,
       c.client_id                                          AS owner_client_id,
       CAST(CONCAT('19', LPAD(c.birth_number
            - IF(MOD(c.birth_number DIV 100, 100) > 50, 5000, 0), 6, '0')) AS DATE) AS owner_birth_date,
       IF(MOD(c.birth_number DIV 100, 100) > 50, 'F', 'M') AS owner_gender,
       (SELECT COUNT(*) FROM disp x
         WHERE x.account_id = a.account_id
           AND x.type = 'DISPONENT')                        AS num_disponents,
       cd.type                                              AS owner_card_type,
       l.loan_id,
       l.amount                                             AS loan_amount,
       l.status                                             AS loan_status,
       CASE l.status
            WHEN 'A' THEN 'Finished, no problems'
            WHEN 'B' THEN 'Finished, loan not paid'
            WHEN 'C' THEN 'Running, OK so far'
            WHEN 'D' THEN 'Running, client in debt'
       END                                                  AS loan_status_desc,
       ROUND(fn_account_balance(a.account_id, NULL), 2)     AS current_balance
FROM account a
JOIN district d  ON d.A1 = a.district_id
JOIN disp dp     ON dp.account_id = a.account_id AND dp.type = 'OWNER'
JOIN client c    ON c.client_id = dp.client_id
LEFT JOIN card cd ON cd.disp_id = dp.disp_id
LEFT JOIN loan l  ON l.account_id = a.account_id;

-- ---------------------------------------------------------------------
-- 8. Test queries (run one by one)
-- ---------------------------------------------------------------------

-- Function
SELECT fn_account_balance(576, '1995-12-31') AS balance_end_1995,
       fn_account_balance(576, NULL)         AS current_balance;

-- Procedure (returns two result sets)
CALL sp_account_statement(576, '1997-01-01', '1997-03-31');

-- View
SELECT * FROM vw_account_overview WHERE loan_status = 'D' LIMIT 20;

-- Trigger 1: insert without trans_id or balance -> trigger fills both
INSERT INTO trans (account_id, `date`, type, operation, amount)
VALUES (576, '1999-01-15', 'PRIJEM', 'VKLAD', 1500);
SELECT * FROM trans WHERE account_id = 576 ORDER BY `date` DESC, trans_id DESC LIMIT 3;

-- Trigger 1: this one must FAIL (negative amount)
-- INSERT INTO trans (account_id, type, amount) VALUES (576, 'VYDAJ', -50);

-- Trigger 2: change a client, check the audit, then revert
UPDATE client SET district_id = 1  WHERE client_id = 1;
UPDATE client SET district_id = 18 WHERE client_id = 1;
SELECT * FROM client_audit WHERE client_id = 1;

-- Clean up the test transaction
DELETE FROM trans WHERE account_id = 576 AND `date` = '1999-01-15' AND amount = 1500;
