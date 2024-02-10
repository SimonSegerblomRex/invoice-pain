"""...

https://www.nordea.com/en/doc/corporate-access-payables-pain-001-examples-v1.8.pdf

"""
import argparse
import dataclasses
import datetime
import json
import time
from pathlib import Path

import toml
from lxml import etree


@dataclasses.dataclass
class Payment:
    """Payment info."""

    issuer: str
    invoice_number: int
    amount: int
    date_due: str
    account_number: str
    currency: str


@dataclasses.dataclass
class Debtor:
    """Debtor info."""

    name: str
    id_nbr: int
    bic: str
    iban: str
    country: str


NSMAP = {
    None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def id_entry(org_nbr):
    id_ = etree.Element("Id")
    org_id = etree.SubElement(id_, "OrgId")
    othr = etree.SubElement(org_id, "Othr")
    etree.SubElement(othr, "Id").text = str(org_nbr)
    return id_


def initg_pty(org_nbr):
    initg_pty = etree.Element("InitgPty")
    initg_pty.append(id_entry(org_nbr))
    id_0 = etree.SubElement(initg_pty, "Id")
    return initg_pty


def credit_transfer(payment):
    cdt_trf_tx_inf = etree.Element("CdtTrfTxInf")
    pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
    etree.SubElement(pmt_id, "InstrId").text = str(payment.invoice_number)
    etree.SubElement(
        pmt_id, "EndToEndId"
    ).text = f"{payment.issuer} {payment.invoice_number}"

    pmt_tp_inf = etree.SubElement(cdt_trf_tx_inf, "PmtTpInf")
    svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
    etree.SubElement(svc_lvl, "Cd").text = "NURG"
    ctgy_purp = etree.SubElement(pmt_tp_inf, "CtgyPurp")
    etree.SubElement(ctgy_purp, "Cd").text = "SUPP"

    amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
    etree.SubElement(amt, "InstdAmt", Ccy=payment.currency).text = str(
        f"{payment.amount:.2f}"
    )

    cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
    fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
    clr_sys_mmb_id = etree.SubElement(fin_instn_id, "ClrSysMmbId")
    clr_sys_id = etree.SubElement(clr_sys_mmb_id, "ClrSysId")
    etree.SubElement(clr_sys_id, "Cd").text = "SESBA"
    etree.SubElement(clr_sys_mmb_id, "MmbId").text = str(9900)

    cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
    etree.SubElement(cdtr, "Nm").text = payment.issuer

    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
    cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
    cdtr_acct_id_othr = etree.SubElement(cdtr_acct_id, "Othr")
    etree.SubElement(cdtr_acct_id_othr, "Id").text = str(payment.account_number)
    schme_nm = etree.SubElement(cdtr_acct_id_othr, "SchmeNm")
    etree.SubElement(schme_nm, "Prtry").text = "BGNR"

    rmt_inf = etree.SubElement(cdt_trf_tx_inf, "RmtInf")
    strd = etree.SubElement(rmt_inf, "Strd")
    cdtr_ref_inf = etree.SubElement(strd, "CdtrRefInf")
    tp = etree.SubElement(cdtr_ref_inf, "Tp")
    cd_or_prtry = etree.SubElement(tp, "CdOrPrtry")
    etree.SubElement(cd_or_prtry, "Cd").text = "SCOR"
    etree.SubElement(cdtr_ref_inf, "Ref").text = str(payment.invoice_number)
    return cdt_trf_tx_inf


def payment_info(debtor, payment):
    pmt_inf = etree.Element("PmtInf")
    etree.SubElement(pmt_inf, "PmtInfId").text = str(payment.invoice_number)
    etree.SubElement(pmt_inf, "PmtMtd").text = "TRF"

    etree.SubElement(pmt_inf, "ReqdExctnDt").text = payment.date_due  # FIXME

    dbtr = etree.SubElement(pmt_inf, "Dbtr")
    nm = etree.SubElement(dbtr, "Nm")
    nm.text = debtor.name
    dbtr.append(id_entry(debtor.id_nbr))
    etree.SubElement(dbtr, "CtryOfRes").text = debtor.country

    dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
    dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
    etree.SubElement(dbtr_acct_id, "IBAN").text = str(debtor.iban)

    dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
    fin_inst_id = etree.SubElement(dbtr_agt, "FinInstnId")
    etree.SubElement(fin_inst_id, "BIC").text = debtor.bic

    cdt_trf_tx_inf = credit_transfer(payment)
    pmt_inf.append(cdt_trf_tx_inf)

    return pmt_inf


class PAINFile:

    """..."""

    def __init__(self, debtor, payments):
        self.debtor = debtor
        self.payments = payments

    @property
    def total_amount(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def group_header(self):
        grp_hdr = etree.Element("GrpHdr")
        etree.SubElement(grp_hdr, "MsgId").text = str(int(time.time()))
        etree.SubElement(grp_hdr, "CreDtTm").text = datetime.datetime.now().isoformat(
            timespec="seconds"
        )
        etree.SubElement(grp_hdr, "NbOfTxs").text = str(len(self.payments))
        etree.SubElement(grp_hdr, "CtrlSum").text = str(f"{self.total_amount:.2f}")
        grp_hdr.append(initg_pty(self.debtor.id_nbr))
        return grp_hdr

    def tmp(self):
        root = etree.Element("Document", nsmap=NSMAP)
        cstmr_cdt_tr_initn = etree.SubElement(root, "CstmrCdtTrfInitn")
        cstmr_cdt_tr_initn.append(self.group_header)

        for payment in self.payments:
            pmt_inf = payment_info(self.debtor, payment)
            cstmr_cdt_tr_initn.append(pmt_inf)

        return root


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="INPUT", help="*.json file", type=Path)
    parser.add_argument("-c", "--config", help="*.toml file", type=Path)
    args = parser.parse_args()

    config = toml.load(args.config)

    with open(args.input, "r") as json_file:
        data = json.load(json_file)
    field_names = set(f.name for f in dataclasses.fields(Payment))
    payments = [
        Payment(**{k: v for k, v in e.items() if k in field_names}) for e in data
    ]

    debtor = Debtor(**config["Debtor"])

    pain = PAINFile(debtor, payments)

    # output_filename = f"{args.input.stem}.xml"
    output_filename = "tmp.xml"
    tree = etree.ElementTree(pain.tmp())
    tree.write(
        output_filename,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )


if __name__ == "__main__":
    _cli()
