import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama
import datetime

# =====================================================================
# AULA PASSO 1: O MÚSCULO (A Função Real)
# =====================================================================
# Esta é a ação real no mundo real (ou no sistema). 
# A IA não roda esse código diretamente. Ela pede para o NOSSO script rodar.
def obter_hora_atual():
    agora = datetime.datetime.now()
    return agora.strftime("%H:%M:%S")

# =====================================================================
# AULA PASSO 2: O MANUAL DE INSTRUÇÕES DA IA (O Schema)
# =====================================================================
# Como a IA sabe que a função acima existe? A gente cria esse "manual" em formato JSON.
# Passamos o NOME exato da função e uma DESCRIÇÃO clara. 
# A IA lê a descrição para tomar a decisão lógica: "O usuário pediu a hora, então preciso usar isso".

ferramenta_hora = {
    'type': 'function',
    'function': {
        'name': 'obter_hora_atual',
        'description': 'Obtém a hora exata atual do relógio do sistema.',
        'parameters': {'type': 'object', 'properties': {}}
    }
}

# O Agente precisa de memória (contexto) para saber o que já aconteceu na conversa.
mensagens = [
    {'role': 'system', 'content': 'Você é um assistente de robótica inteligente. Responda sempre em português do Brasil de forma clara e amigável.'}
]

# --- 3. Lógica da Interface e Integração ---
def atualizar_chat(texto, tag):
    """Função auxiliar para inserir texto colorido no chat"""
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, texto + "\n\n", tag)
    chat_box.yview(tk.END) # Rola a tela para o final
    chat_box.config(state=tk.DISABLED)

def processar_mensagem(pergunta):
    """Roda em background para não travar a tela"""
    mensagens.append({'role': 'user', 'content': pergunta})
    
    try:
        atualizar_chat("🤖 Processando...", "sistema_info")
        
        # =====================================================================
        # AULA PASSO 3: A DECISÃO (A Primeira Chamada)
        # =====================================================================
        # Mandamos a pergunta E o manual de instruções (tools=[ferramenta_hora]).
        # A IA pensa: "Posso responder isso sozinho ou preciso do manual?"
        resposta = ollama.chat(model='qwen2.5:3b', messages=mensagens, tools=[ferramenta_hora])
        mensagens.append(resposta['message'])

        # =====================================================================
        # AULA PASSO 4: A EXECUÇÃO (Tool Calling)
        # =====================================================================
        # Verificamos: A IA devolveu uma resposta de texto normal, ou devolveu um PEDIDO 
        # para usar a ferramenta? (Isso é o tool_calls).
        if resposta.get('message', {}).get('tool_calls'):
            for tool in resposta['message']['tool_calls']:

                # A IA pediu especificamente para rodar 'obter_hora_atual'?
                if tool['function']['name'] == 'obter_hora_atual':
                    
                    # --- FEEDBACK VISUAL DA FERRAMENTA ---
                    atualizar_chat("⚙️ [AÇÃO]: Agente acionou a ferramenta 'obter_hora_atual'...", "ferramenta")
                    
                    # Executa a ferramenta
                    hora_do_sistema = obter_hora_atual()
                    
                    # Mostra o resultado da ferramenta na tela
                    atualizar_chat(f"✅ [SENSOR]: A ferramenta leu a hora: {hora_do_sistema}. Gerando resposta...", "ferramenta")
                    
                    # =====================================================================
                    # AULA PASSO 5: O RETORNO DO SENSOR
                    # =====================================================================
                    # Agora pegamos o resultado bruto (ex: 15:30:00) e avisamos a IA:
                    # "Aqui está o dado que você pediu!". O 'role' agora é 'tool'.
                    mensagens.append({
                        'role': 'tool',
                        'content': f"O relógio do sistema informou que agora são {hora_do_sistema}",
                        'name': 'obter_hora_atual'
                    })
                    
                    # Segunda chamada para gerar a fala final
                    resposta_final = ollama.chat(model='qwen2.5:3b', messages=mensagens)
                    mensagens.append(resposta_final['message'])
                    
                    # Imprime a resposta final
                    atualizar_chat(f"Agente: {resposta_final['message']['content']}", "bot")
        else:
            # Se não usou ferramenta, apenas imprime a resposta
            atualizar_chat(f"Agente: {resposta['message']['content']}", "bot")
            
    except Exception as e:
        atualizar_chat(f"❌ Erro de conexão: {e}", "erro")

def enviar(event=None):
    texto_usuario = entrada.get()
    if not texto_usuario.strip(): return
    
    # Exibe o que o usuário digitou
    atualizar_chat(f"Você: {texto_usuario}", "usuario")
    entrada.delete(0, tk.END) # Limpa a caixa de texto
    
    # Cria uma Thread para a interface não congelar enquanto o Ollama pensa
    threading.Thread(target=processar_mensagem, args=(texto_usuario,), daemon=True).start()

# --- 4. Construção da Interface Gráfica (Tkinter Dark Mode) ---
root = tk.Tk()
root.title("Terminal Robótico - Agente Qwen")
root.geometry("550x650")
root.configure(bg="#1E1E1E") # Fundo cinza escuro

# Área do Chat
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, 
                                     bg="#1E1E1E", fg="#D4D4D4", 
                                     font=("Consolas", 11), bd=0, padx=10, pady=10)
chat_box.pack(fill=tk.BOTH, expand=True)

# Configuração de Cores e Estilos (As "Tags")
chat_box.tag_config("usuario", foreground="#5CE1E6", font=("Consolas", 12, "bold")) # Ciano
chat_box.tag_config("bot", foreground="#FFFFFF", font=("Consolas", 12))             # Branco
chat_box.tag_config("ferramenta", foreground="#FF9F1C", font=("Consolas", 10, "italic")) # Laranja
chat_box.tag_config("sistema_info", foreground="#6c757d", font=("Consolas", 10))    # Cinza discreto
chat_box.tag_config("erro", foreground="#FF4C4C", font=("Consolas", 11, "bold"))    # Vermelho

# Caixa de Entrada de Texto
frame_entrada = tk.Frame(root, bg="#1E1E1E", pady=10, padx=10)
frame_entrada.pack(fill=tk.X)

entrada = tk.Entry(frame_entrada, font=("Consolas", 12), bg="#2D2D2D", fg="white", 
                   insertbackground="white", relief=tk.FLAT)
entrada.pack(fill=tk.X, ipady=10)
entrada.bind("<Return>", enviar) # Permite enviar apertando o "Enter"

atualizar_chat("🟢 Sistema online. Agente carregado na memória. Digite algo abaixo.", "sistema_info")

root.mainloop()