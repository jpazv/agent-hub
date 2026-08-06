"""Cliente somente-leitura do Metabase.

Toda query passa por aqui. O guarda em `_assert_readonly` existe porque a
restricao do projeto e dura: nada pode ser escrito no BD Grupo Velas.
"""
from __future__ import annotations

import io
import json
import os
import pathlib
import re
import time

import pandas as pd
import requests

BASE_URL = os.environ.get("METABASE_URL", "https://metabase.grupovelas.com.br")
DATABASE_ID = int(os.environ.get("METABASE_DB_ID", "2"))

_SESSION_FILE = pathlib.Path(__file__).parent / ".metabase_session"

# Qualquer um destes no SQL aborta antes de sair da maquina.
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|truncate|alter|create|grant|revoke|"
    r"refresh|vacuum|copy|call|do|comment)\b",
    re.IGNORECASE,
)


def get_session() -> str:
    token = os.environ.get("METABASE_SESSION")
    if token:
        return token.strip()
    if _SESSION_FILE.exists():
        return _SESSION_FILE.read_text().strip()
    raise RuntimeError(
        "Sessao do Metabase nao encontrada. Defina METABASE_SESSION ou grave o "
        f"token em {_SESSION_FILE}"
    )


def _assert_readonly(sql: str) -> None:
    stripped = re.sub(r"--[^\n]*", " ", sql)
    stripped = re.sub(r"/\*.*?\*/", " ", stripped, flags=re.DOTALL)
    hit = _FORBIDDEN.search(stripped)
    if hit:
        raise RuntimeError(f"Query bloqueada: contem '{hit.group(0)}'. Este projeto e somente-leitura.")
    if not re.match(r"^\s*(select|with)\b", stripped, re.IGNORECASE):
        raise RuntimeError("Query bloqueada: deve comecar com SELECT ou WITH.")


def _payload(sql: str) -> dict:
    return {"database": DATABASE_ID, "type": "native", "native": {"query": sql}}


def query_df(sql: str, retries: int = 3) -> pd.DataFrame:
    """Executa SQL e devolve DataFrame.

    Usa /api/dataset/csv porque o endpoint JSON trunca em 2.000 linhas.
    format_rows=false mantem numeros e datas crus (sem formatacao pt-BR,
    que quebraria o parse).
    """
    _assert_readonly(sql)
    url = f"{BASE_URL}/api/dataset/csv"
    headers = {"X-Metabase-Session": get_session()}
    data = {"query": json.dumps(_payload(sql)), "format_rows": "false"}

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=900)
            if resp.status_code == 202:
                time.sleep(3)
                continue
            resp.raise_for_status()
            # O Metabase devolve text/csv sem charset; por RFC o requests assume
            # ISO-8859-1 e o portugues acentuado vira mojibake ("OlÃ¡").
            resp.encoding = "utf-8"
            text = resp.text
            if text.lstrip().startswith("{") and '"error"' in text[:400]:
                raise RuntimeError(f"Metabase devolveu erro: {text[:500]}")
            return pd.read_csv(io.StringIO(text), low_memory=False)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Falha apos {retries} tentativas: {last_err}")


def check_session() -> bool:
    try:
        df = query_df("select 1 as ok")
        return not df.empty
    except Exception:  # noqa: BLE001
        return False
