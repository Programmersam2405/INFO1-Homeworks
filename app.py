from datetime import date, datetime
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
    "Acompanhe suas tarefas. O progresso marcado aqui é salvo para não se"
    " perder ao atualizar a página!"
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

    # Seção para Adicionar Tarefa
    st.subheader("➕ Adicionar Nova")
    nova_tarefa = st.text_input(
        "Atividade:", placeholder="Ex: Livro de História pág. 40"
    )
    prazo_tarefa = st.date_input("Data limite (Prazo):", value=date.today())

    if st.button("Publicar para todo mundo"):
      if nova_tarefa.strip():
        tarefa_obj = {
            "texto": nova_tarefa.strip(),
            "prazo": prazo_tarefa.strftime("%Y-%m-%d"),
        }
        tarefas_mestre.append(tarefa_obj)
        salvar_tarefas_mestre(tarefas_mestre)
        st.success("Atividade publicada com sucesso!")
        st.rerun()
      else:
        st.warning("Digite uma atividade válida.")

    if tarefas_mestre:
      # Seção para Atualizar Prazo
      st.divider()
      st.subheader("✏️ Atualizar Prazo")

      opcoes_atualizacao = []
      for idx, t in enumerate(tarefas_mestre):
        if isinstance(t, str):
          opcoes_atualizacao.append(f"{idx}: {t} (Sem prazo)")
        else:
          opcoes_atualizacao.append(
              f"{idx}: {t.get('texto', '')} (Prazo:"
              f" {t.get('prazo', 'N/D')})"
          )

      tarefa_para_atualizar = st.selectbox(
          "Selecione a tarefa para mudar o prazo:",
          opcoes_atualizacao,
          key="select_atualizar_prazo",
      )
      novo_prazo = st.date_input(
          "Novo prazo:", value=date.today(), key="data_novo_prazo"
      )

      if st.button("💾 Salvar novo prazo"):
        idx_atualizar = int(tarefa_para_atualizar.split(":")[0])
        tarefa_atual = tarefas_mestre[idx_atualizar]

        if isinstance(tarefa_atual, str):
          texto_t = tarefa_atual
        else:
          texto_t = tarefa_atual.get("texto", "")

        tarefas_mestre[idx_atualizar] = {
            "texto": texto_t,
            "prazo": novo_prazo.strftime("%Y-%m-%d"),
        }
        salvar_tarefas_mestre(tarefas_mestre)
        st.success("Prazo atualizado com sucesso!")
        st.rerun()

      # Seção para Excluir Tarefa
      st.divider()
      st.subheader("🗑️ Gerenciar / Excluir")

      opcoes_exclusao = []
      for idx, t in enumerate(tarefas_mestre):
        if isinstance(t, str):
          opcoes_exclusao.append(f"{idx}: {t}")
        else:
          opcoes_exclusao.append(f"{idx}: {t.get('texto', '')}")

      tarefa_selecionada = st.selectbox(
          "Selecione a tarefa para apagar:",
          opcoes_exclusao,
          key="select_excluir",
      )

      if st.button("❌ Excluir tarefa selecionada"):
        idx_para_remover = int(tarefa_selecionada.split(":")[0])
        tarefas_mestre.pop(idx_para_remover)
        salvar_tarefas_mestre(tarefas_mestre)
        st.success("Tarefa excluída com sucesso!")
        st.rerun()

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
  # Inicializa o progresso individual e recupera dos query_params se já existirem
  if "progresso_individual" not in st.session_state:
    st.session_state.progresso_individual = {}
    saved_progress = st.query_params.get("progresso", "")
    if saved_progress:
      for idx_str in saved_progress.split(","):
        if idx_str.isdigit():
          st.session_state.progresso_individual[int(idx_str)] = True

  hoje = date.today()
  indices_concluidos = []

  # Mostra as tarefas com caixas de seleção e verificação de prazo
  for i, tarefa in enumerate(tarefas_mestre):
    if isinstance(tarefa, str):
      texto_tarefa = tarefa
      prazo_str = None
    else:
      texto_tarefa = tarefa.get("texto", "")
      prazo_str = tarefa.get("prazo", None)

    status_atual = st.session_state.progresso_individual.get(i, False)

    # Verifica se o prazo expirou
    expirado = False
    texto_prazo_exibicao = ""
    if prazo_str:
      data_prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date()
      texto_prazo_exibicao = f" *(Prazo: {data_prazo.strftime('%d/%m/%Y')})*"
      if hoje > data_prazo:
        expirado = True

    # Monta o visual da checkbox com o aviso se expirou
    label = f"**{texto_tarefa}**{texto_prazo_exibicao}"
    if expirado:
      label += " 🔴 **[Data limite atingida]**"

    concluida = st.checkbox(label, value=status_atual, key=f"user_task_{i}")
    st.session_state.progresso_individual[i] = concluida

    if concluida:
      indices_concluidos.append(str(i))

  # Salva o progresso atualizado nos parâmetros da URL para persistir ao atualizar
  if indices_concluidos:
    st.query_params["progresso"] = ",".join(indices_concluidos)
  else:
    if "progresso" in st.query_params:
      del st.query_params["progresso"]
