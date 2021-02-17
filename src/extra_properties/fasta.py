#! /usr/bin/python3

import os
import sys
import logging

sys.path.insert(1, "../../")
from db import session, Protein, Fasta, Similarity
from utils import download_fasta


def save_fasta(idcode: str, pid: int) -> None:
    exists_fasta = session.query(Fasta.pid).filter_by(pid=pid).first()
    if exists_fasta:
        logging.info(f"{idcode} fasta file already exists.")
        return

    fasta_file = download_fasta(idcode, pid)
    new_fasta = Fasta(pid=pid, fasta_file=fasta_file)
    session.add(new_fasta)
    session.commit()


def get_similar_idcodes(idcode: str, pid: int, seqid: float = 0.9) -> list:
    output_f = f"alnRes_{idcode}.m8"
    cmd = f"mmseqs easy-search {idcode} ~/Download/mmseqs/bin/DB_PDB {output_f} tmp --min-seq-id {seqid} --max-seqs 1000000"
    os.system(cmd)

    similar = []
    with open(output_f) as f:
        for line in f:
            exc_idcode, _ = line.strip().split()[1].split("_")
            if exc_idcode != idcode:
                similar.append(exc_idcode)

    os.system(f"rm {idcode} {output_f}")

    return similar


def save_similar_idcodes(idcode: str, pid: int, seqid: float = 0.9):

    exists_cluster = session.query(Similarity.pid).filter_by(pid=pid).first()
    if exists_cluster:
        logging.info(f"{idcode} similarity cluster already exists.")
        return

    similar = get_similar_idcodes(idcode, pid, seqid=seqid)

    new_cluster = Similarity(pid=pid, cluster=similar, seqid=seqid)
    session.add(new_cluster)
    session.commit()


if __name__ == "__main__":
    # for idcode in idcodes_to_process("urgent_idcodes"):

    idcode = sys.argv[1]
    print("############", idcode, "############")

    pid = session.query(Protein.pid).filter_by(idcode=idcode).first()[0]

    save_fasta(idcode, pid)
    run_mmseqs(idcode, pid)