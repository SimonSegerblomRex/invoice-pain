"""Script for generating pain."""
import argparse
import dataclasses
import datetime
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import toml

import date_finder


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
    "xmlns": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def id_entry(org_nbr):
    id_ = ET.Element("Id")
    org_id = ET.SubElement(id_, "OrgId")
    othr = ET.SubElement(org_id, "Othr")
    ET.SubElement(othr, "Id").text = str(org_nbr)  # FIXME: .replace("-", "") or not..?
    return id_


def initg_pty(org_nbr):
    initg_pty = ET.Element("InitgPty")
    initg_pty.append(id_entry(org_nbr))
    return initg_pty


def credit_transfer(payment):
    cdt_trf_tx_inf = ET.Element("CdtTrfTxInf")
    pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
    ET.SubElement(pmt_id, "InstrId").text = str(payment.invoice_number)
    ET.SubElement(
        pmt_id, "EndToEndId"
    ).text = f"{payment.issuer} {payment.invoice_number}"[:35]

    pmt_tp_inf = ET.SubElement(cdt_trf_tx_inf, "PmtTpInf")
    svc_lvl = ET.SubElement(pmt_tp_inf, "SvcLvl")
    ET.SubElement(svc_lvl, "Cd").text = "NURG"
    ctgy_purp = ET.SubElement(pmt_tp_inf, "CtgyPurp")
    ET.SubElement(ctgy_purp, "Cd").text = "SUPP"

    amt = ET.SubElement(cdt_trf_tx_inf, "Amt")
    ET.SubElement(amt, "InstdAmt", Ccy=payment.currency).text = str(
        f"{payment.amount:.2f}"
    )

    cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
    fin_instn_id = ET.SubElement(cdtr_agt, "FinInstnId")
    clr_sys_mmb_id = ET.SubElement(fin_instn_id, "ClrSysMmbId")
    clr_sys_id = ET.SubElement(clr_sys_mmb_id, "ClrSysId")
    ET.SubElement(clr_sys_id, "Cd").text = "SESBA"
    ET.SubElement(clr_sys_mmb_id, "MmbId").text = str(
        9900
    )  # FIXME: Hard-coded for Bankgiro

    cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
    ET.SubElement(cdtr, "Nm").text = payment.issuer

    cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
    cdtr_acct_id = ET.SubElement(cdtr_acct, "Id")
    cdtr_acct_id_othr = ET.SubElement(cdtr_acct_id, "Othr")
    ET.SubElement(cdtr_acct_id_othr, "Id").text = str(payment.account_number)
    schme_nm = ET.SubElement(cdtr_acct_id_othr, "SchmeNm")
    ET.SubElement(schme_nm, "Prtry").text = "BGNR"

    rmt_inf = ET.SubElement(cdt_trf_tx_inf, "RmtInf")
    strd = ET.SubElement(rmt_inf, "Strd")
    cdtr_ref_inf = ET.SubElement(strd, "CdtrRefInf")
    tp = ET.SubElement(cdtr_ref_inf, "Tp")
    cd_or_prtry = ET.SubElement(tp, "CdOrPrtry")
    ET.SubElement(cd_or_prtry, "Cd").text = "SCOR"
    ET.SubElement(cdtr_ref_inf, "Ref").text = str(payment.invoice_number)
    return cdt_trf_tx_inf


def payment_info(debtor, payment):
    pmt_inf = ET.Element("PmtInf")
    ET.SubElement(pmt_inf, "PmtInfId").text = str(payment.invoice_number)
    ET.SubElement(pmt_inf, "PmtMtd").text = "TRF"

    ET.SubElement(pmt_inf, "ReqdExctnDt").text = payment.date_due

    dbtr = ET.SubElement(pmt_inf, "Dbtr")
    nm = ET.SubElement(dbtr, "Nm")
    nm.text = debtor.name
    dbtr.append(id_entry(debtor.id_nbr))
    ET.SubElement(dbtr, "CtryOfRes").text = debtor.country

    dbtr_acct = ET.SubElement(pmt_inf, "DbtrAcct")
    dbtr_acct_id = ET.SubElement(dbtr_acct, "Id")
    ET.SubElement(dbtr_acct_id, "IBAN").text = str(debtor.iban)

    dbtr_agt = ET.SubElement(pmt_inf, "DbtrAgt")
    fin_inst_id = ET.SubElement(dbtr_agt, "FinInstnId")
    ET.SubElement(fin_inst_id, "BIC").text = debtor.bic

    cdt_trf_tx_inf = credit_transfer(payment)
    pmt_inf.append(cdt_trf_tx_inf)
    return pmt_inf


class PAINFile:

    """PAIN."""

    def __init__(self, debtor, payments):
        self.debtor = debtor
        self.payments = payments
        self.timestamp = datetime.datetime.now()

    @property
    def total_amount(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def group_header(self):
        grp_hdr = ET.Element("GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = str(int(self.timestamp.timestamp()))
        ET.SubElement(grp_hdr, "CreDtTm").text = self.timestamp.isoformat(
            timespec="seconds"
        )
        ET.SubElement(grp_hdr, "NbOfTxs").text = str(len(self.payments))
        ET.SubElement(grp_hdr, "CtrlSum").text = str(f"{self.total_amount:.2f}")
        grp_hdr.append(initg_pty(self.debtor.id_nbr))
        return grp_hdr

    def generate_xml(self):
        root = ET.Element("Document", **NSMAP)
        cstmr_cdt_tr_initn = ET.SubElement(root, "CstmrCdtTrfInitn")
        cstmr_cdt_tr_initn.append(self.group_header)

        for payment in self.payments:
            pmt_inf = payment_info(self.debtor, payment)
            cstmr_cdt_tr_initn.append(pmt_inf)

        return ET.ElementTree(root)


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

    bank_days = date_finder.BankDays(debtor.country)
    last_bank_day_of_month = bank_days.last_bank_day_of_current_month()
    next_bank_day = bank_days.next_bank_day()
    # Update date_due
    for payment in payments:
        date_due = datetime.date.fromisoformat(payment.date_due)
        if date_due <= next_bank_day:
            payment.date_due = str(next_bank_day)
        elif date_due >= last_bank_day_of_month:
            payment.date_due = str(last_bank_day_of_month)

    pain = PAINFile(debtor, payments)

    tree = pain.generate_xml()
    output_filename = f"pain-{int(pain.timestamp.timestamp())}.xml"
    ET.indent(tree)
    tree.write(
        output_filename,
        encoding="utf-8",
        xml_declaration=True,
    )


if __name__ == "__main__":
    _cli()
