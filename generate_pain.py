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

def initg_pty(org_nbr):
    initg_pty = etree.Element("InitgPty")
    id_0 = etree.SubElement(initg_pty, "Id")
    org_id = etree.SubElement(id_0, "OrgId")
    othr = etree.SubElement(org_id, "Othr")
    id_1 = etree.SubElement(othr, "Id")
    id_1.text = str(org_nbr)
    return initg_pty


def payment(amount, ocr, date):
    pmt_inf = etree.Element("PmtInf")
    pmt_inf_id = etree.SubElement(pmt_inf, "PmtInfId")
    pmt_inf_id.text = "Tmp text"  # FIXME
    pmt_mtd = etree.SubElement(pmt_inf, "PmtMtd")
    pmt_mtd.text = "TRF"
    #<ReqdExctnDt>2020-10-31</ReqdExctnDt>
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

    payment_0 = payment(500, 1234, "")
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
