import json
import os
import streamlit as st

ARQUIVO_TAREFAS = "tarefas_mestre.json"

# Defina a sua senha secreta de administrador aqui:
SENHA_ADMIN = "rNUeKNs.9JhADnF"


def carregar_tarefas_mestre():
  if os.path.exists(ARQUIVO_TAREFAS):
    with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


def salvar_tarefas_mestre(tarefas):
  with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
    json.dump(tarefas, f, ensure_ascii=False, indent=4)


st.set_page_config(page_title="Gerenciador de Tarefas da Turma", page_icon="📚")

st.title("📚 Atividades e Para-casa")
st.write(
    "Acompanhe suas tarefas. O progresso marcado aqui é apenas seu e fica"
    " salvo no seu navegador!"
)

# Carrega a lista oficial de tarefas criada pelo admin
tarefas_mestre = carregar_tarefas_mestre()

# --- ÁREA DO ADMINISTRADOR (Na barra lateral) ---
with st.sidebar:
  st.header("🔒 Painel do Criador")
  senha_digitada = st.text_input(
      "Senha para adicionar tarefas:", type="password"
  )

  if senha_digitada == SENHA_ADMIN:
    st.success("Modo Admin Ativado! ✅")
    nova_tarefa = st.text_input(
        "Nova atividade:", placeholder="Ex: Livro de História pág. 40"
    )

    if st.button("➕ Publicar para todo mundo"):
      if nova_tarefa.strip():
        tarefas_mestre.append(nova_tarefa.strip())
        salvar_tarefas_mestre(tarefas_mestre)
        st.success("Atividade publicada com sucesso!")
        st.rerun()
      else:
        st.warning("Digite uma atividade válida.")
  elif senha_digitada:
    st.error("Senha incorreta!")

st.divider()

# --- ÁREA DE EXIBIÇÃO PARA OS USUÁRIOS ---
st.subheader("📋 Lista de Atividades:")

if not tarefas_mestre:
  st.info(
      "Ainda não há nenhuma atividade cadastrada pelo administrador. Volte"
      " mais tarde! 🎉"
  )
else:
  # Inicializa o progresso individual na sessão do navegador da pessoa que abriu o site
  if "progresso_individual" not in st.session_state:
    st.session_state.progresso_individual = {}

  # Mostra as tarefas com caixas de seleção independentes por usuário
  for i, texto_tarefa in enumerate(tarefas_mestre):
    status_atual = st.session_state.progresso_individual.get(i, False)

    concluida = st.checkbox(
        f"**{texto_tarefa}**", value=status_atual, key=f"user_task_{i}"
    )

    # Atualiza o status apenas na memória daquele usuário específico
    st.session_state.progresso_individual[i] = concluida
