"""...

https://www.nordea.com/en/doc/corporate-access-payables-pain-001-examples-v1.8.pdf

"""
import argparse
import datetime
from dataclasses import dataclass
from pathlib import Path

from lxml import etree
import toml


@dataclass
class Payment:
    """Receiver info."""

    id: int
    gross: float


@dataclass
class Common:
    """Common info."""

    orgnbr: int
    period: str

NSMAP = {
    None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def id_entry(org_nbr):
    id_0 = etree.Element("Id")
    org_id = etree.SubElement(id_0, "OrgId")
    othr = etree.SubElement(org_id, "Othr")
    id_1 = etree.SubElement(othr, "Id")
    id_1.text = str(org_nbr)
    return id_0


def initg_pty(org_nbr):
    initg_pty = etree.Element("InitgPty")
    initg_pty.append(id_entry(org_nbr))
    id_0 = etree.SubElement(initg_pty, "Id")
    return initg_pty


def payment(amount, ocr, date):
    pmt_inf = etree.Element("PmtInf")
    pmt_inf_id = etree.SubElement(pmt_inf, "PmtInfId")
    pmt_inf_id.text = "Tmp text"  # FIXME
    pmt_mtd = etree.SubElement(pmt_inf, "PmtMtd")
    pmt_mtd.text = "TRF"
    reqd_extn_dt = etree.SubElement(pmt_inf, "ReqdExctnDt")
    reqd_extn_dt.text = date.isoformat()

    dbtr = etree.SubElement(pmt_inf, "Dbtr")
    nm = etree.SubElement(dbtr, "Nm")
    nm.text = "Fixme"  # FIXME
    dbtr.append(id_entry(888))  #FIXME org_nbr
    ctry_of_res = etree.SubElement(dbtr, "CtryOfRes")
    ctry_of_res.text = "SE"  # FIXME

    dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
    dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
    dbtr_iban = etree.SubElement(dbtr_acct_id, "IBAN")
    dbtr_iban.text = str(88)  # FIXME

    dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
    fin_inst_id = etree.SubElement(dbtr_agt, "FinInstnId")
    bic = etree.SubElement(fin_inst_id, "BIC")
    bic.text= "HANDSESS" # FIXME

    cdt_trf_tx_inf = etree.SubElement(pmt_inf, "CdtTrfTxInf")
    pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
    instr_id = etree.SubElement(pmt_id, "InstrId")
    instr_id.text = "FIXME"  # FIXME
    end_to_end_id = etree.SubElement(pmt_id, "EndToEndId")
    end_to_end_id.text = "FIXME"  # FIXME

    pmt_tp_inf = etree.SubElement(cdt_trf_tx_inf, "PmtTpInf")
    svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
    etree.SubElement(svc_lvl, "Cd").text = "NURG"
    ctgy_purp = etree.SubElement(pmt_tp_inf, "CtgyPurp")
    etree.SubElement(ctgy_purp, "Cd").text = "SUPP"

    amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
    etree.SubElement(amt, "InstdAmt", Ccy="SEK").text = str(f"{100:.2f}")  # FIXME

    cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
    fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
    clr_sys_mmb_id = etree.SubElement(fin_instn_id, "ClrSysMmbId")
    clr_sys_id = etree.SubElement(clr_sys_mmb_id, "ClrSysId")
    etree.SubElement(clr_sys_id, "Cd").text = "SESBA"
    etree.SubElement(clr_sys_mmb_id, "MmbId").text = str(9900)

    cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
    etree.SubElement(cdtr, "Nm").text = "Mottagarnamn"  # FIXME

    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
    cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
    cdtr_acct_id_othr = etree.SubElement(cdtr_acct_id, "Othr")
    etree.SubElement(cdtr_acct_id_othr, "Id").text = str(12345)  # FIXME: bankgiro!?!
    schme_nm = etree.SubElement(cdtr_acct_id_othr, "SchmeNm")
    etree.SubElement(schme_nm, "Prtry").text = "BGNR"

    rmt_inf = etree.SubElement(cdt_trf_tx_inf, "RmtInf")
    strd = etree.SubElement(rmt_inf, "Strd")
    cdtr_ref_inf = etree.SubElement(strd, "CdtrRefInf")
    tp = etree.SubElement(cdtr_ref_inf, "Tp")
    cd_or_prtry = etree.SubElement(tp, "CdOrPrtry")
    etree.SubElement(cd_or_prtry, "Cd").text = "SCOR"
    etree.SubElement(cdtr_ref_inf, "Ref").text = str(1234)  # FIXME: OCR

    return pmt_inf


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="INPUT", help="*.toml file", type=Path)
    args = parser.parse_args()

    root = etree.Element("Document", nsmap=NSMAP)

    # Group header
    grp_hdr = etree.Element("GrpHdr")
    msg_id = etree.SubElement(grp_hdr, "MsgId")
    msg_id.text = str(1)  # FIXME
    cre_dt_tm = etree.SubElement(grp_hdr, "CreDtTm")
    cre_dt_tm.text = datetime.datetime.now().isoformat(timespec="seconds")
    nbr_of_txs = etree.SubElement(grp_hdr, "NbOfTxs")
    nbr_of_txs.text = str(1)  # FIXME
    ctrl_sum = etree.SubElement(grp_hdr, "CtrlSum")
    ctrl_sum.text = str(f"{1000:.2f}")  # FIXME
    grp_hdr.append(initg_pty(11111))  # FIXME

    cstmr_cdt_tr_initn = etree.SubElement(root, "CstmrCdtTrfInitn")
    cstmr_cdt_tr_initn.append(grp_hdr)

    payment_0 = payment(500, 1234, datetime.date(2024, 2, 29))
    cstmr_cdt_tr_initn.append(payment_0)

    #output_filename = f"{args.input.stem}.xml"
    output_filename = "tmp.xml"
    tree = etree.ElementTree(root)
    tree.write(
        output_filename,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )

    """
    # Skattverket's parser doesn't like single quotes...
    # https://github.com/lxml/lxml/pull/277
    with open(output_filename, "r+b") as f:
        old = f.readline()
        new = old.replace(b"'", b'"')
        f.seek(0)
        f.write(new)
    """


if __name__ == "__main__":
    _cli()
