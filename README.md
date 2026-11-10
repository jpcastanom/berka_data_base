# Berka Data Base

Database design for managing bank customers, their accounts and the financial operations performed on them.

**Authors:** Juan Felipe Molano Vega, Juan Pablo Castaño Morales

## Brief description

This project models a relational database for a bank. It stores customers, the accounts they hold, the transactions made on those accounts, standing payment orders, loans and issued cards. It also stores demographic data for each district, so financial behavior can be analyzed against the characteristics of the area where customers and branches are located.

## Context

A bank needs a database to administer the information about its customers, their accounts and the financial operations carried out on them. The data is organized around the following entities.

- **Customer:** identifier, date of birth, gender and district of residence.
- **District:** name, region, population, number of municipalities, degree of urbanization, average salary, unemployment rate and number of entrepreneurs. It complements customer and account data with demographic information.
- **Account:** identifier, opening date, district of the branch and the frequency of its account statements.
- **Disposition:** the link between a customer and an account. A customer can have several accounts and an account can be used by several customers. The disposition states whether the customer is the **owner** or only an **authorized user**.
- **Transaction:** date, type of movement, operation performed, amount and resulting balance. When applicable, it also records the counterparty bank and account. An account can have many transactions, which gives its history and balance evolution.
- **Payment order (standing order):** originating account, destination bank and account, amount sent and the type or purpose of the payment. An account can have several orders.
- **Loan:** grant date, amount, duration, periodic installment and status. An account has at most one loan. The status distinguishes four cases:
  - finished without problems,
  - finished with payment problems,
  - running with no issues,
  - running with the customer in debt.
- **Card:** identifier, type and issue date. Each card is tied to a disposition, so it identifies both the account it can operate on and the customer entitled to use it.

## What the database should answer

- Which accounts belong to each customer.
- Who is authorized to operate each account.
- Which cards have been issued.
- The transaction history of an account.
- The standing payment orders of an account.
- The loans granted.
- How financial behavior relates to district demographics.

## Repository contents

The repository is currently empty apart from this file. The conceptual model, attribute characterization and implementation scripts will be added as the project progresses.
