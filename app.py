# app.py
# Versão 33: Foco em personalização estratégica, com seleção de plataforma, tom e expressão.

import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Estúdio de Conteúdo IA", page_icon="🧠")

# --- ESTILO CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-18ni7ap { background-color: #111827; }
    .stButton>button {
        background-color: #4F46E5; color: white; border-radius: 0.5rem; border: none;
        padding: 10px 20px; font-weight: bold; transition: background-color 0.2s;
    }
    .stButton>button:hover { background-color: #4338CA; }
    .result-card {
        background-color: #1F2937; border: 1px solid #374151; border-radius: 0.75rem;
        padding: 20px; margin-bottom: 10px; height: 100%;
    }
    .result-card h4 {
        color: #C4B5FD; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #374151; padding-bottom: 8px;
    }
    .stMetric {
        background-color: #1F2937;
        border-radius: 0.75rem;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL PARA CONFIGURAÇÃO DA API ---
st.sidebar.title("Configuração")
st.sidebar.markdown("Para usar a aplicação, por favor, insira a sua chave de API da Google.")
api_key_input = st.sidebar.text_input("Sua Chave de API da Google", type="password", help="Pode obter a sua chave no Google AI Studio ou Google Cloud Console.")

# --- LÓGICA DE CONFIGURAÇÃO DA API ---
api_key_configured = False
if api_key_input:
    try:
        genai.configure(api_key=api_key_input)
        api_key_configured = True
        st.sidebar.success("API configurada com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao configurar a API: {e}")

# --- FUNÇÃO PARA CHAMAR A API ---
def call_gemini_api(prompt_text, schema):
    if not api_key_configured:
        st.error("Por favor, configure a sua chave de API na barra lateral para continuar.")
        return None
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        safe_prompt = prompt_text + "\n\nInstrução Crítica: O texto gerado em todos os campos NUNCA deve conter aspas duplas. Use aspas simples (') se for estritamente necessário. É mandatório que todos os campos do schema JSON sejam preenchidos."
        response = model.generate_content(safe_prompt)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Ocorreu um erro ao chamar a API: {e}")
        return None

def call_gemini_vision_api(prompt_text, image, schema):
    if not api_key_configured:
        st.error("Por favor, configure a sua chave de API na barra lateral para continuar.")
        return None
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            [prompt_text, image],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Ocorreu um erro ao chamar a API com imagem: {e}")
        return None


# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'product_desc' not in st.session_state:
    st.session_state.product_desc = ""

# --- INTERFACE PRINCIPAL ---
st.title("Estúdio de Conteúdo ✨ IA")
st.markdown("<p style='color:#9CA3AF;'>O seu centro de comando para marketing de afiliados.</p>", unsafe_allow_html=True)

if api_key_configured:
    tab_package, tab_analysis, tab_angles, tab_optimizer, tab_responses = st.tabs([
        "📦 Pacote de Conteúdo", "📊 Análise de Concorrente", "🎯 Ângulos de Marketing", "✍️ Otimizador de Copy", "✉️ Respostas"
    ])

    with tab_package:
        st.header("📦 Gerador de Pacote de Conteúdo Personalizado")
        st.write("Descreva o seu produto, defina a sua estratégia e receba um pacote de conteúdo completo com um clique.")
        
        product_desc_package = st.text_area("1. Descreva o seu produto ou cole o link da Shopee:", placeholder="Ex: Mini aspirador de pó portátil para carro, potente e recarregável via USB.", key="product_desc_package", height=100)
        
        st.write("2. Defina a sua Estratégia de Comunicação:")
        col1, col2, col3 = st.columns(3)
        with col1:
            platforms = st.multiselect("Plataformas", ["Reels/TikTok", "Threads", "Pinterest"], default=["Reels/TikTok", "Threads"])
        with col2:
            tone = st.selectbox("Tom de Voz", ["Exagerado & Pessoal", "Engraçado & Irónico", "Informativo & Confiável"])
        with col3:
            expression = st.selectbox("Expressão Emocional", ["Espanto & Descoberta", "Urgência & Escassez", "Humor & Sarcasmo"])

        if st.button("Gerar Pacote de Conteúdo!", key="btn_package"):
            if product_desc_package and platforms:
                with st.spinner("A IA está a criar o seu pacote de conteúdo..."):
                    prompt = f"""
                    Aja como uma agência de marketing especialista em conteúdo viral para afiliados.
                    Para o produto '{product_desc_package}', crie um pacote de conteúdo para as plataformas: {', '.join(platforms)}.
                    A comunicação deve seguir estritamente a seguinte estratégia:
                    - Tom de Voz: {tone}
                    - Expressão Emocional: {expression}
                    - Foco: Despertar curiosidade e desejo de compra imediato, com textos curtos e de alto impacto.
                    - Regra Crítica: O texto gerado NUNCA deve conter aspas duplas.

                    Gere um objeto JSON com uma chave para cada plataforma selecionada.
                    - Para 'Reels/TikTok', forneça 'legenda' e 'sugestao_audio'.
                    - Para 'Threads', forneça uma 'legenda' curta e provocadora.
                    - Para 'Pinterest', forneça um 'titulo' curto e chamativo.
                    """
                    
                    # Schema dinâmico com base nas plataformas selecionadas
                    properties = {}
                    if "Reels/TikTok" in platforms:
                        properties["reels_tiktok"] = {"type": "OBJECT", "properties": {"legenda": {"type": "STRING"}, "sugestao_audio": {"type": "STRING"}}}
                    if "Threads" in platforms:
                        properties["threads"] = {"type": "OBJECT", "properties": {"legenda": {"type": "STRING"}}}
                    if "Pinterest" in platforms:
                        properties["pinterest"] = {"type": "OBJECT", "properties": {"titulo": {"type": "STRING"}}}

                    schema = {"type": "OBJECT", "properties": properties}
                    
                    results = call_gemini_api(prompt, schema)
                    if results:
                        st.subheader("🚀 O seu Pacote de Conteúdo Personalizado está Pronto!")
                        
                        if "reels_tiktok" in results:
                            content = results["reels_tiktok"]
                            st.markdown(f"<div class='result-card'><h4>🚀 Reels & TikTok</h4><p style='font-size:18px; font-weight:bold;'>{content.get('legenda', 'N/A')}</p><p style='font-size:14px; color:#9CA3AF; margin-top:10px;'><strong>Áudio Sugerido:</strong> {content.get('sugestao_audio', 'N/A')}</p></div>", unsafe_allow_html=True)
                        
                        if "threads" in results:
                            content = results["threads"]
                            st.markdown(f"<div class='result-card'><h4>💬 Threads</h4><p style='font-size:18px; font-weight:bold;'>{content.get('legenda', 'N/A')}</p></div>", unsafe_allow_html=True)

                        if "pinterest" in results:
                            content = results["pinterest"]
                            st.markdown(f"<div class='result-card'><h4>📌 Pinterest (Título)</h4><p style='font-size:18px; font-weight:bold;'>{content.get('titulo', 'N/A')}</p></div>", unsafe_allow_html=True)
            else:
                st.warning("Por favor, descreva o produto e selecione pelo menos uma plataforma.")

    with tab_analysis:
        st.header("📊 Análise de Concorrente")
        st.write("Cole a descrição de um post viral e a IA fará uma 'engenharia reversa' do sucesso.")
        competitor_post = st.text_area("Descrição ou legenda do post concorrente:", placeholder="Ex: Cole aqui o texto do Reels viral que você viu sobre um produto de cozinha...", height=150, key="competitor_post")
        if st.button("Analisar Concorrente", key="btn_analysis"):
            if competitor_post:
                with st.spinner("Analisando os segredos do concorrente..."):
                    prompt = f"Aja como um analista de marketing viral. Analise o seguinte post: '{competitor_post}'. Identifique e retorne: 'gancho_usado' (o tipo de gancho, ex: Curiosidade, Problema/Solução), 'apelo_emocional' (o sentimento principal explorado) e 'cta_utilizado' (a chamada para ação). O texto não deve conter aspas duplas. Retorne um objeto JSON."
                    schema = {"type": "OBJECT", "properties": {"gancho_usado": {"type": "STRING"}, "apelo_emocional": {"type": "STRING"}, "cta_utilizado": {"type": "STRING"}}}
                    result = call_gemini_api(prompt, schema)
                    if result:
                        st.subheader("Análise Estratégica:")
                        st.metric("🧠 Tipo de Gancho", result.get('gancho_usado', 'N/A'))
                        st.metric("❤️ Apelo Emocional", result.get('apelo_emocional', 'N/A'))
                        st.metric("👉 Chamada para Ação (CTA)", result.get('cta_utilizado', 'N/A'))
            else: st.warning("Por favor, insira a descrição do post concorrente.")

    with tab_angles:
        st.header("🎯 Brainstorm de Ângulos de Marketing")
        product_desc_angles = st.text_area("Descreva o seu produto:", value=st.session_state.product_desc, key="product_desc_angles", height=100)
        if st.button("Gerar Ângulos", key="btn_angles"):
            if product_desc_angles:
                with st.spinner("Criando novos ângulos de marketing..."):
                    prompt = f"Aja como um estratega de marketing. Para o produto '{product_desc_angles}', crie 4 ângulos de marketing distintos. Para cada um, forneça um 'angulo' (o nome da estratégia) e uma 'ideia_de_video' (uma frase que resuma o vídeo). O texto não deve conter aspas duplas. Retorne uma lista de objetos JSON."
                    schema = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"angulo": {"type": "STRING"}, "ideia_de_video": {"type": "STRING"}}}}
                    results = call_gemini_api(prompt, schema)
                    if results:
                        st.subheader("Novos Ângulos para Explorar:")
                        cols = st.columns(len(results) if len(results) <= 4 else 4)
                        for i, angle in enumerate(results):
                            with cols[i % 4]:
                                st.markdown(f"<div class='result-card'><h4>{angle.get('angulo', '')}</h4><p>{angle.get('ideia_de_video', '')}</p></div>", unsafe_allow_html=True)
            else: st.warning("Por favor, descreva o produto.")

    with tab_optimizer:
        st.header("✍️ Otimizador de Copy (Revisor IA)")
        st.write("Escreva a sua própria legenda ou narração e deixe a IA melhorá-la para a tornar mais viral.")
        original_text = st.text_area("Cole o seu texto original aqui:", height=150, placeholder="Ex: Compre este novo produto, é muito bom e útil para o seu dia a dia...", key="optimizer_text")
        if st.button("Otimizar Texto", key="btn_optimizer"):
            if original_text:
                with st.spinner("Otimizando a sua copy..."):
                    prompt = f"Aja como um copywriter de topo. Reescreva o seguinte texto para o tornar mais persuasivo e viral: '{original_text}'. O texto não deve conter aspas duplas. Retorne um objeto JSON com a chave 'texto_otimizado'."
                    schema = {"type": "OBJECT", "properties": {"texto_otimizado": {"type": "STRING"}}}
                    result = call_gemini_api(prompt, schema)
                    if result:
                        st.subheader("Resultado da Otimização:")
                        st.markdown("<div class='result-card' style='border-left: 4px solid #10B981;'><h4>Versão Otimizada pela IA:</h4><p>" + result.get('texto_otimizado', 'N/A') + "</p></div>", unsafe_allow_html=True)
            else: st.warning("Por favor, insira um texto para otimizar.")
            
    with tab_responses:
        st.header("✉️ Gerador de Respostas")
        comment_input = st.text_area("Cole o comentário do seguidor:", placeholder="Ex: Quanto custa? Manda o link!", key="comment_input")
        if st.button("Gerar Respostas", key="btn_responses"):
            if comment_input:
                with st.spinner("Pensando na resposta..."):
                    prompt = f"Para o comentário '{comment_input}', crie 3 respostas amigáveis que direcionem para o 'link na bio'. O texto não deve conter aspas duplas. Retorne um JSON com uma lista de strings."
                    schema = {"type": "ARRAY", "items": {"type": "STRING"}}
                    results = call_gemini_api(prompt, schema)
                    if results:
                        st.subheader("Sugestões de Resposta:")
                        for response in results:
                            st.markdown(f"<div class='result-card'><p>{response}</p></div>", unsafe_allow_html=True)
            else: st.warning("Por favor, insira um comentário.")

else:
    st.warning("👋 Bem-vindo ao Estúdio de Conteúdo IA!")
    st.info("Para começar, por favor, insira a sua chave de API da Google na barra lateral à esquerda.")

