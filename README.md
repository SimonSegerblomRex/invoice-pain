Invoice PAIN
============

Introduction
------------
This script has the sole purpose of generating ISO 20022 compliant XML files that can be uploaded to [Handelsbanken](https://www.handelsbanken.se/)'s ["Filtjänster"](https://www.handelsbanken.se/sv/foretag/konton-betalningar/tjanster-som-forenklar/filtjanster) to issue Bankgiro payments.
As of 2024 Handelsbanken relies on the standard [pain.001.001.03](https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pain.001.001.03) from 2009.
(It seems like most other Swedish banks also have implemented this standard, but with different quirks.)

Usage
-----
Run the script with:
```shell
python3 generate_pain.py transactions.json -c debtor.toml
```

Example of `transactions.json`:
```json
[
    {
        "issuer": "E.ON Kundsupport Sverige AB",
        "amount": 6749,
        "date_due": "2024-03-05",
        "invoice_number": 56731420313,
        "account_number": "5014-0045",
        "category": "El",
        "currency": "SEK"
    },
    {
        "issuer": "VA SYD",
        "amount": 4074,
        "date_due": "2024-02-29",
        "invoice_number": 848012498,
        "account_number": "5976-0702",
        "category": "Vatten och avfall",
        "currency": "SEK"
    }
]
```

Required keys for each transaction:
* issuer
* date_due
* invoice_number
* account_number
* currency

(Any additional keys will be ignored by the script.)

One recommended way to create this file is to use [invoice2data](https://github.com/invoice-x/invoice2data) with custom templates:
```shell
invoice2data --exclude-built-in-templates --template-folder <path to template directory> --output-format json --output-name transactions <input directory>/*.pdf
```

Example of `debtor.toml`:
```toml
[Debtor]
name = "Company Name"
id_nbr = "000000-0000"  # Organization number
bic = "HANDSESS"
iban = "SE0000000000000000000000"
country = "SE"
```

Verify the output *.xml-file with:
```shell
sudo apt install libxml2-utils
xmllint pain.xml --schema pain.001.001.03.xsd
```
after downloading `pain.001.001.03.xsd`
from [Handelsbanken](https://www.handelsbanken.se/tron/public/info/contents/v1/document/32-109749?targetGroups=OFFICE)
and/or from [iso20022.org](https://www.iso20022.org/message/14316/download).

References
----------
* [Recommendations from Handelsbanken when implementing ISO 20022 pain.001](https://www.handelsbanken.com/tron/xgpu/info/contents/v1/document/72-111388)
* [ISO 20022 CustomerCreditTransferInitiation Pain.001 version 3 Country Specific Information](https://www.handelsbanken.com/tron/xgpu/info/contents/v1/document/72-111386)
* [Björn Lundén: Betalfilsformat – ISO 20022](https://support.bjornlunden.se/guide/betalfilsformat-iso-20022)
* [Handelsbanken ISO 20022 pain.001 ver 3 example](https://www.handelsbanken.com/tron/xgpu/info/contents/v1/document/72-109749)
* [Nordea Message Implementation Guidelines pain.001.001.03](https://www.nordea.com/en/doc/nordea-message-implementation-guide-pain-001.001.03-payments.pdf)
