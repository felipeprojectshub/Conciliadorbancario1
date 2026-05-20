"""
Script para limpar o banco de dados:
- Exclui TODAS as empresas (clientes) e seus dados relacionados (depara, templates)
- Exclui TODOS os usuários exceto felipe.r@jcacontadores.com.br
- Limpa logs e histórico de depara

Uso:
    python scripts/limpar_banco.py
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "conciliador.db"

ADMIN_EMAIL = "felipe.r@jcacontadores.com.br"


def main():
    if not DB_PATH.exists():
        print(f"ERRO: Banco não encontrado em {DB_PATH}")
        sys.exit(1)

    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row

    # ── Mostrar estado atual ─────────────────────────────────────────────
    print("=" * 60)
    print("ESTADO ATUAL DO BANCO")
    print("=" * 60)

    usuarios = con.execute("SELECT id, email, perfil, ativo FROM usuarios").fetchall()
    print(f"\nUsuários ({len(usuarios)}):")
    for u in usuarios:
        print(f"  [{u['id']}] {u['email']} (perfil={u['perfil']}, ativo={u['ativo']})")

    clientes = con.execute("SELECT id, nome FROM clientes").fetchall()
    print(f"\nEmpresas ({len(clientes)}):")
    for c in clientes:
        print(f"  [{c['id']}] {c['nome']}")

    depara_count = con.execute("SELECT COUNT(*) FROM depara").fetchone()[0]
    templates_count = con.execute("SELECT COUNT(*) FROM conciliacao_templates").fetchone()[0]
    logs_count = con.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    print(f"\nRegras De-Para: {depara_count}")
    print(f"Templates: {templates_count}")
    print(f"Logs: {logs_count}")

    # ── Confirmar ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("AÇÕES QUE SERÃO EXECUTADAS:")
    print("  1. Excluir TODAS as empresas e dados relacionados")
    print(f"  2. Excluir todos os usuários EXCETO {ADMIN_EMAIL}")
    print("  3. Limpar logs e histórico de depara")
    print("=" * 60)

    resp = input("\nConfirmar limpeza? (s/N): ").strip().lower()
    if resp != "s":
        print("Cancelado pelo usuário.")
        sys.exit(0)

    # ── Executar limpeza ─────────────────────────────────────────────────
    con.execute("DELETE FROM depara")
    print("✓ Tabela depara limpa")

    con.execute("DELETE FROM conciliacao_templates")
    print("✓ Tabela conciliacao_templates limpa")

    con.execute("DELETE FROM clientes")
    print("✓ Tabela clientes limpa")

    deleted_users = con.execute(
        "DELETE FROM usuarios WHERE email != ?", (ADMIN_EMAIL,)
    ).rowcount
    print(f"✓ {deleted_users} usuário(s) excluído(s) (mantido: {ADMIN_EMAIL})")

    # Limpar histórico
    try:
        con.execute("DELETE FROM depara_historico")
        print("✓ Tabela depara_historico limpa")
    except Exception:
        pass

    con.execute("DELETE FROM logs")
    print("✓ Tabela logs limpa")

    con.commit()
    con.close()

    # ── Verificar resultado ──────────────────────────────────────────────
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row

    print("\n" + "=" * 60)
    print("ESTADO FINAL DO BANCO")
    print("=" * 60)

    usuarios = con.execute("SELECT id, email, perfil, ativo FROM usuarios").fetchall()
    print(f"\nUsuários ({len(usuarios)}):")
    for u in usuarios:
        print(f"  [{u['id']}] {u['email']} (perfil={u['perfil']}, ativo={u['ativo']})")

    clientes = con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    depara = con.execute("SELECT COUNT(*) FROM depara").fetchone()[0]
    print(f"\nEmpresas: {clientes}")
    print(f"Regras De-Para: {depara}")
    print(f"\n✅ Limpeza concluída com sucesso!")

    con.close()


if __name__ == "__main__":
    main()
