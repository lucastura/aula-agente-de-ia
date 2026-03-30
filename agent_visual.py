import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama
import datetime
import os
import platform

# =====================================================================
# 1. OS MÚSCULOS (As funções reais em Python)
# =====================================================================
def obter_hora_atual():
    agora = datetime.datetime.now()
    return agora.strftime("%H:%M:%S")

def desligar_computador():
    """Identifica o sistema operacional e envia o comando de desligamento com aviso."""
    sistema = platform.system()
    if sistema == "Windows":
        os.system("shutdown /s /t 15") # Desliga em 15 segundos
        return "Comando de desligamento iniciado. O Windows será desligado em 15 segundos."
    elif sistema == "Linux":
        os.system("shutdown +1") # Desliga em 1 minuto no Linux
        return "Comando de desligamento iniciado. O Linux será desligado em 1 minuto."
    else:
        return "Sistema operacional não reconhecido para desligamento."

# =====================================================================
# 2. OS MANUAIS DE INSTRUÇÃO (Os Schemas para a IA)
# =====================================================================
ferramenta_hora = {
    'type': 'function',
    'function': {
        'name': 'obter_hora_atual',
        'description': 'Obtém a hora exata atual do relógio do sistema do computador.',
        'parameters': {'type': 'object', 'properties': {}}
    }
}

ferramenta_desligar = {
    'type': 'function',
    'function': {
        'name': 'desligar_computador',
        'description': 'Desliga o computador.',
        'parameters': {'type': 'object', 'properties': {}}
    }
}

# =====================================================================
# 3. MEMÓRIA E CONFIGURAÇÃO DA IA
# =====================================================================
# O System Prompt define a personalidade e as regras básicas do agente
mensagens = [
    {'role': 'system', 'content': 'Você é um assistente de robótica inteligente e proativo. Responda sempre em português do Brasil de forma clara e amigável.'}
]

# =====================================================================
# 4. LÓGICA DE INTEGRAÇÃO E INTERFACE
# =====================================================================
def atualizar_chat(texto, tag):
    """Insere o texto no chat com a cor e estilo corretos"""
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, texto + "\n\n", tag)
    chat_box.yview(tk.END)
    chat_box.config(state=tk.DISABLED)

def processar_mensagem(pergunta):
    """Roda em background para não congelar a interface visual"""
    mensagens.append({'role': 'user', 'content': pergunta})
    
    try:
        atualizar_chat("🤖 Pensando...", "sistema_info")
        
        # PASSO A: Mandamos a pergunta e as DUAS ferramentas disponíveis
        resposta = ollama.chat(
            model='qwen2.5:3b', 
            messages=mensagens, 
            tools=[ferramenta_hora, ferramenta_desligar]
        )
        mensagens.append(resposta['message'])

        # PASSO B: A IA decidiu usar alguma ferramenta?
        if resposta.get('message', {}).get('tool_calls'):
            for tool in resposta['message']['tool_calls']:
                
                nome_ferramenta = tool['function']['name']
                resultado_ferramenta = ""
                
                # --- Roteamento: Qual ferramenta ela escolheu? ---
                if nome_ferramenta == 'obter_hora_atual':
                    atualizar_chat("⚙️ [AÇÃO]: Agente acionou o relógio do sistema...", "ferramenta")
                    resultado_ferramenta = obter_hora_atual()
                    atualizar_chat(f"✅ [SENSOR]: Hora lida: {resultado_ferramenta}", "ferramenta")
                    
                elif nome_ferramenta == 'desligar_computador':
                    atualizar_chat("⚠️ [AÇÃO CRÍTICA]: Agente iniciou protocolo de desligamento...", "erro")
                    resultado_ferramenta = desligar_computador()
                    atualizar_chat(f"✅ [SISTEMA]: {resultado_ferramenta}", "erro")
                
                # PASSO C: Devolvemos o resultado da ação para a IA ler
                mensagens.append({
                    'role': 'tool',
                    'content': f"Resultado da ação: {resultado_ferramenta}",
                    'name': nome_ferramenta
                })
                
                # PASSO D: Segunda chamada para a IA formular a fala final com base no resultado
                resposta_final = ollama.chat(model='qwen2.5:3b', messages=mensagens)
                mensagens.append(resposta_final['message'])
                
                atualizar_chat(f"Agente: {resposta_final['message']['content']}", "bot")
        else:
            # Se não precisou de ferramenta, responde normalmente
            atualizar_chat(f"Agente: {resposta['message']['content']}", "bot")
            
    except Exception as e:
        atualizar_chat(f"❌ Erro de conexão: {e}", "erro")

def enviar(event=None):
    texto_usuario = entrada.get()
    if not texto_usuario.strip(): return
    
    atualizar_chat(f"Você: {texto_usuario}", "usuario")
    entrada.delete(0, tk.END)
    
    threading.Thread(target=processar_mensagem, args=(texto_usuario,), daemon=True).start()

# =====================================================================
# 5. CONSTRUÇÃO DA INTERFACE GRÁFICA (Dark Mode)
# =====================================================================
root = tk.Tk()
root.title("Terminal Robótico - Agente Qwen")
root.geometry("600x700")
root.configure(bg="#1E1E1E")

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, 
                                     bg="#1E1E1E", fg="#D4D4D4", 
                                     font=("Consolas", 11), bd=0, padx=10, pady=10)
chat_box.pack(fill=tk.BOTH, expand=True)

# Cores do terminal
chat_box.tag_config("usuario", foreground="#5CE1E6", font=("Consolas", 12, "bold"))
chat_box.tag_config("bot", foreground="#FFFFFF", font=("Consolas", 12))
chat_box.tag_config("ferramenta", foreground="#FF9F1C", font=("Consolas", 10, "italic"))
chat_box.tag_config("sistema_info", foreground="#6c757d", font=("Consolas", 10))
chat_box.tag_config("erro", foreground="#FF4C4C", font=("Consolas", 11, "bold"))

frame_entrada = tk.Frame(root, bg="#1E1E1E", pady=10, padx=10)
frame_entrada.pack(fill=tk.X)

entrada = tk.Entry(frame_entrada, font=("Consolas", 12), bg="#2D2D2D", fg="white", 
                   insertbackground="white", relief=tk.FLAT)
entrada.pack(fill=tk.X, ipady=10)
entrada.bind("<Return>", enviar)

atualizar_chat("🟢 Sistema online. Módulos de Tempo e Energia carregados.\nDigite um comando abaixo.", "sistema_info")

root.mainloop()