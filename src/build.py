"""
Gera o site do Cris Rozzini (maquiador e cabeleireiro, Ribeirão Preto) em dist/.

Cada página de src/pages começa com um comentário de metadados:
<!--meta {"title": "...", "description": "...", "nav": "sobre", "theme": "dark"} -->

Marcadores disponíveis dentro das páginas:
  {{ARROW}}               seta dos botões
  {{ICON:nome}}           ícone
  {{WA}}                  link do WhatsApp com mensagem padrão
  {{WA_FONE}}             telefone do WhatsApp por extenso
  {{IG}} {{IG_CAZA}}      Instagram do Cris e do salão
  {{ENDERECO}}            endereço do CAZA
  {{ROTA}}                link de rota no Google Maps
  {{MAPA}}                mapa incorporado
  {{RAIL:cat}}            vitrine de reels de uma categoria (ou "destaque")
  {{REEL:id}}             um reel solto (retrato que toca)
  {{GALERIA}}             galeria completa com filtros (reels + fotos)
  {{SERVICOS_LISTA}}      lista de serviços com prévia de foto (home)
  {{SERVICOS_CARDS}}      cartões completos dos serviços
  {{PASSOS}}              passo a passo do atendimento
  {{CTA_BG}}              colunas de fotos que correm atrás do CTA final
  {{FORM}}                formulário de agendamento que vai para o WhatsApp

Uso:  python src/build.py
"""
import json
import pathlib
import re
from html import escape
from urllib.parse import quote, quote_plus

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
OUT = ROOT / "dist"
SITE = "https://crisrozzini.achillesmedia.com.br"
V = "3"  # versão dos arquivos estáticos; aumente a cada publicação de CSS ou JS

# ------------------------------------------------------------------
# Dados. Altere aqui e rode o build de novo.
# ------------------------------------------------------------------
PERFIL = {
    "nome": "Cris Rozzini",
    "wa": "5516997866939",
    "wa_fone": "(16) 99786-6939",
    "instagram": "https://www.instagram.com/crisrozzini/",
    "instagram_caza": "https://www.instagram.com/cazabelezaporcrisrozzini/",
    "salao": "CAZA Beleza por Cris Rozzini",
    "rua": "Rua Adolfo Serra, 603",
    "bairro": "Alto da Boa Vista",
    "cidade": "Ribeirão Preto, SP",
}
PERFIL["q"] = f"{PERFIL['rua']}, {PERFIL['bairro']}, {PERFIL['cidade']}"
WA_MSG = "Olá, Cris! Vim pelo site e gostaria de agendar um horário."

NAV = [  # (chave, rótulo, arquivo, aparece no topo)
    ("index", "Início", "index.html", False),
    ("sobre", "Sobre", "sobre.html", True),
    ("trabalhos", "Trabalhos", "trabalhos.html", True),
    ("servicos", "Serviços", "servicos.html", True),
    ("caza", "O CAZA", "caza.html", True),
    ("agendamento", "Agendamento", "agendamento.html", True),
    ("contato", "Contato", "contato.html", True),
]

CATS = [("noivas", "Noivas"), ("convidadas", "Madrinhas e convidadas"), ("debutantes", "15 anos e formaturas"), ("bastidores", "Bastidores")]
CAT_NOME = dict(CATS)

# Reels do Instagram do Cris. id = código do post; textos curtos escritos a partir das legendas.
REELS = [
    ("DRAGuUTEaDq", "debutantes", "Sofia, formatura", "Vermelho para o jantar da graduação em Medicina: cachos presos e pele luminosa."),
    ("DbD1sTBREH9", "noivas", "Viviane, noiva", "Nem todo pôr do sol acontece no horizonte. Às vezes, a poucos passos do altar."),
    ("DgFpSydRGS1", "convidadas", "Lu, convidada", "Cabelo e maquiagem com vestido Gloria Coelho. Sempre um espetáculo."),
    ("DZTdQFIxwIM", "convidadas", "Lu, de perto", "Olho esfumado, pele acetinada e rabo de cavalo polido."),
    ("DbPRBoex4lv", "noivas", "Isabela, noiva", "A deslumbrante noiva do dia, entrando para o sim."),
    ("DZQ0ZY8RGX2", "convidadas", "Flávia, convidada", "Bom gosto absurdo e postura leve: o retoque final do batom é do Cris."),
    ("Ddy2d60xR--", "convidadas", "Josy, tia do noivo", "Diva de Giorgio Armani para o casamento do sobrinho."),
    ("DPcY-NWEZUs", "noivas", "Lara, noiva", "Véu longo, cerimônia entre flores brancas."),
    ("DYqJ_SbRAyL", "convidadas", "Josy, em vermelho", "Cabelo e maquiagem em harmonia com o look, as joias e a identidade dela."),
    ("DaY5BBPR1TU", "noivas", "Ingrid, noiva", "Penteado e maquiagem para a cerimônia na igreja."),
    ("DfA8cQ1xklB", "convidadas", "Flávia, de plumas", "Elegância natural, do coque baixo ao brilho dos brincos."),
    ("DXCQ4n7EQWF", "noivas", "Moniara, noiva", "Cabelo assinado pelo Cris para a entrada na catedral."),
    ("Da_ZpN-xPr0", "noivas", "Viviane, o sim", "A noiva da semana, sob os lustres do salão."),
    ("DQ_1IvWkb91", "debutantes", "Sofia, missa", "O primeiro dos eventos da formatura em Medicina."),
    ("DawPBh6x2nB", "debutantes", "Família Salomão", "Técnica, experiência e afeto: três gerações cuidadas pelo Cris."),
    ("DQSfiHMETuE", "convidadas", "Duda, dupla produção", "Sábado como madrinha, domingo nos 60 anos do pai."),
    ("DddxVPjxCl7", "noivas", "Duda, uma década", "Há mais de dez anos acompanhando os grandes momentos dela."),
    ("DO9BHLwkZOk", "bastidores", "Flávia para a Um Tok", "Editorial de moda com beleza do Cris."),
    ("DfP4oA9OV4J", "bastidores", "Na Casa Affonso", "O Cris abre a nécessaire e mostra o que usa em cada produção."),
    ("DfSzBPEhOKa", "bastidores", "Na Festa Pode?", "Spoiler do bate-papo no podcast sobre noivas e emoção."),
    ("DXu877bkamW", "bastidores", "Fadas Madrinhas", "A equipe do CAZA produzindo as meninas do Hospital de Amor."),
]
REEL = {r[0]: r for r in REELS}

FOTOS = [
    ("DbV0Rt1RpBe-0", "noivas", "Isabela, noiva", "Um sonho de renda e véu."),
    ("DaxdsmokTvR-1", "debutantes", "Sofia, 15 anos", "Cor, corte, maquiagem e penteado."),
    ("DNddpBntWEs-0", "convidadas", "Josy", "Ondas largas e pele de cetim."),
    ("DaxdsmokTvR-0", "debutantes", "Sofia, 15 anos", "Uma verdadeira princesa."),
    ("DNJrU2MtIvJ-0", "debutantes", "Amanda, colação", "Pronta para a colação de grau em Medicina."),
    ("DRDVdWYkf7f-0", "debutantes", "Sofia, colação", "O terceiro evento da formatura."),
    ("DaxdsmokTvR-5", "bastidores", "Ajuste final", "O Cris confere cada mecha antes da entrada."),
    ("DNeeLmsNBYN-0", "convidadas", "Maria Goretti", "Alegria, com ou sem batom vermelho."),
    ("DaxdsmokTvR-3", "debutantes", "Sofia, 15 anos", "Valsa sob as luzes douradas."),
    ("DRuCZwgkcdU-0", "bastidores", "15 anos em Ribeirão", "Desde 1º de dezembro de 2010 criando laços."),
    ("DaxdsmokTvR-4", "debutantes", "Sofia, 15 anos", "O bolo, as velas e o brilho."),
    ("DQWxM3sETLo-0", "bastidores", "Fixação", "Força na peruca que a semana promete."),
    ("DYLFGuIkSIm-0", "convidadas", "Josy, Feijoada do Bem", "Produção no aniversário de 7 anos do CAZA."),
    ("DSqK8_6kXuD-0", "bastidores", "Equipe CAZA", "Mãos que cuidam e corações que acreditam."),
]

SERVICOS = [
    {"id": "noivas", "nome": "Noivas", "img": "img/fotos/DbV0Rt1RpBe-0.jpg",
     "curto": "Beleza completa para o grande dia, do teste ao último retoque antes do sim.",
     "texto": "Cabelo e maquiagem pensados junto com o vestido, as joias e o estilo da cerimônia. Tudo testado antes, para que no dia só exista emoção.",
     "itens": ["Conversa de visagismo", "Teste de cabelo e maquiagem", "Produção no CAZA ou no local", "Acompanhamento até a entrada"],
     "tags": ["Cabelo", "Maquiagem", "Dia da noiva"]},
    {"id": "convidadas", "nome": "Madrinhas e convidadas", "img": "img/reels/DgFpSydRGS1.jpg",
     "curto": "Mães, madrinhas e convidadas com a mesma assinatura da noiva.",
     "texto": "Produções que conversam com o look, a paleta da festa e o horário do evento. Ideal para combinar a família inteira.",
     "itens": ["Penteados presos, semipresos ou soltos", "Maquiagem de longa duração", "Agenda para grupos", "Produção de mãe e pai dos noivos"],
     "tags": ["Casamentos", "Festas", "Eventos"]},
    {"id": "debutantes", "nome": "15 anos e formaturas", "img": "img/fotos/DaxdsmokTvR-1.jpg",
     "curto": "Debutantes, colações e bailes: beleza que acompanha a valsa até o fim.",
     "texto": "Do primeiro corte à produção da festa, o Cris cuida da imagem da debutante e da formanda em cada evento da celebração.",
     "itens": ["Cor, corte, maquiagem e penteado", "Missa, colação e baile", "Ensaio fotográfico", "Troca de visual na festa"],
     "tags": ["15 anos", "Medicina", "Baile"]},
    {"id": "cabelo", "nome": "Cabelo", "img": "img/fotos/DNddpBntWEs-0.jpg",
     "curto": "Corte, cor, escova e ondas assinados pelo Cris no dia a dia.",
     "texto": "Cabelos de mulheres e homens que querem um visual elegante todos os dias, não só nos dias de festa.",
     "itens": ["Corte feminino e masculino", "Coloração e iluminação", "Escova e ondas", "Tratamentos e tricologia no CAZA"],
     "tags": ["Corte", "Cor", "Tricologia"]},
    {"id": "maquiagem", "nome": "Maquiagem social", "img": "img/reels/DZTdQFIxwIM.jpg",
     "curto": "Pele impecável e olhar marcante para jantares, ensaios e eventos.",
     "texto": "Maquiagem feita para a luz do evento e para a câmera, com produtos de alta performance e acabamento que dura a noite inteira.",
     "itens": ["Jantares e eventos sociais", "Ensaios e editoriais", "Gravações e entrevistas", "Maquiagem masculina"],
     "tags": ["Eventos", "Ensaios", "Masculino"]},
    {"id": "visagismo", "nome": "Visagismo e imagem", "img": "img/reels/DYqJ_SbRAyL.jpg",
     "curto": "Formação em Visagismo e Consultoria de Imagem pela École Française Look By Lia.",
     "texto": "Uma imagem sofisticada nunca é feita de partes soltas. Cabelo e maquiagem precisam dialogar com a roupa, as joias e a identidade de quem usa.",
     "itens": ["Análise de rosto e estilo", "Harmonia com look e joias", "Mudança de visual", "Consultoria para eventos"],
     "tags": ["Visagismo", "Consultoria"]},
]

PASSOS = [
    ("Conversa", "Você conta a data, o evento e o que imagina. O primeiro contato é pelo WhatsApp."),
    ("Visagismo", "O Cris estuda o rosto, o look, as joias e o horário para desenhar a produção certa."),
    ("Teste", "Para noivas e debutantes, um teste antes do dia deixa tudo resolvido sem pressa."),
    ("O grande dia", "Produção no CAZA ou no local do evento, com tempo para respirar e se emocionar."),
]

FORM_SERVICOS = ["Noiva", "Madrinha ou mãe dos noivos", "Convidada", "15 anos", "Formatura", "Maquiagem social",
                 "Penteado", "Corte e cor", "Visagismo", "Outro"]

_S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
ICONS = {
    "arrow": f'<svg class="arrow" {_S}><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "up": f'<svg {_S}><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
    "close": f'<svg {_S}><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    "pin": f'<svg {_S}><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "route": f'<svg {_S}><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h7a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h7"/></svg>',
    "calendar": f'<svg {_S}><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    "clock": f'<svg {_S}><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    "sparkle": f'<svg {_S}><path d="M12 3c.6 4.2 2.8 6.4 7 7-4.2.6-6.4 2.8-7 7-.6-4.2-2.8-6.4-7-7 4.2-.6 6.4-2.8 7-7z"/><path d="M19 16c.2 1.4.9 2.1 2.3 2.3-1.4.2-2.1.9-2.3 2.3-.2-1.4-.9-2.1-2.3-2.3 1.4-.2 2.1-.9 2.3-2.3z"/></svg>',
    "brush": f'<svg {_S}><path d="M14.5 4.5 19.5 9.5 11 18a3 3 0 0 1-4.2 0L6 17.2a3 3 0 0 1 0-4.2z"/><path d="M6 17.2 3.5 20.5"/><path d="M12.5 6.5l5 5"/></svg>',
    "heart": f'<svg {_S}><path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.4a4.3 4.3 0 0 1 7.5 2.4C19.5 15.4 12 20 12 20z"/></svg>',
    "award": f'<svg {_S}><circle cx="12" cy="9" r="5.5"/><path d="M8.5 13.3 7 21l5-2.6 5 2.6-1.5-7.7"/></svg>',
    "instagram": f'<svg {_S}><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/></svg>',
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.79-1.47-1.76-1.65-2.05-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.6-.92-2.2-.24-.58-.49-.5-.67-.5h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.3 1.27.49 1.7.63.72.23 1.37.2 1.88.12.57-.09 1.75-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.45 9.45 0 0 1-4.82-1.32l-.35-.2-3.58.94.96-3.49-.23-.36a9.43 9.43 0 0 1-1.45-5.03c0-5.22 4.25-9.47 9.48-9.47 2.53 0 4.9.99 6.7 2.78a9.4 9.4 0 0 1 2.77 6.7c0 5.23-4.25 9.45-9.47 9.45zm8.06-17.52A11.33 11.33 0 0 0 12.05.64C5.77.64.66 5.75.66 12.03c0 2 .52 3.96 1.52 5.69L.57 23.6l6.03-1.58a11.36 11.36 0 0 0 5.44 1.39h.01c6.28 0 11.39-5.11 11.39-11.39 0-3.04-1.18-5.9-3.33-8.05z"/></svg>',
}
ARROW = ICONS["arrow"]
SWATCHES = [("#5c0f26", "Vinho"), ("#a3243f", "Bordô"), ("#c96f8b", "Rosé"), ("#e49ab0", "Rosa"), ("#f4d3dc", "Blush"), ("#1a0c10", "Ébano")]


def wa(msg=WA_MSG):
    return f"https://wa.me/{PERFIL['wa']}?text={quote(msg)}"


def map_embed():
    return f"https://www.google.com/maps?q={quote_plus(PERFIL['q'])}&output=embed"


def route_link():
    return f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(PERFIL['q'])}"


def a(s):
    return escape(s, quote=True)


def reel(rid, extra=""):
    _, cat, titulo, cap = REEL[rid]
    return (f'<button type="button" class="reel{extra}" data-full="assets/video/full/{rid}.mp4" data-title="{a(titulo)}" '
            f'data-cap="{a(cap)}" data-cat="{a(CAT_NOME[cat])}" data-ig="https://www.instagram.com/reel/{rid}/" aria-label="Assistir: {a(titulo)}">'
            f'<img src="assets/img/reels/{rid}.jpg" alt="{a(titulo)}: {a(cap)}" loading="lazy" width="720" height="1280">'
            f'<video muted loop playsinline preload="none" data-src="assets/video/p/{rid}.mp4"></video>'
            f'<span class="reel-play">{ICONS["play"]}</span>'
            f'<span class="reel-info"><span class="label">{CAT_NOME[cat]}</span><strong>{titulo}</strong></span></button>')


DESTAQUE = ["DRAGuUTEaDq", "DbD1sTBREH9", "DZQ0ZY8RGX2", "DgFpSydRGS1", "DbPRBoex4lv", "Ddy2d60xR--", "DZTdQFIxwIM",
            "DPcY-NWEZUs", "DYqJ_SbRAyL", "DfA8cQ1xklB", "DaY5BBPR1TU"]


def rail(cat):
    ids = DESTAQUE if cat == "destaque" else [r[0] for r in REELS if r[2] and r[1] == cat]
    items = "".join(reel(i) for i in ids)
    return f'<div class="reel-rail" data-rail>{items}</div>'


def galeria():
    counts = {c: 0 for c, _ in CATS}
    tiles = []
    # intercala reels e fotos para o mosaico ficar variado
    rs = [r for r in REELS if r[1] != "bastidores" or r[0] in ("DfP4oA9OV4J", "DXu877bkamW")]
    fs = list(FOTOS)
    while rs or fs:
        for _ in range(2):
            if rs:
                rid, cat, titulo, cap = rs.pop(0)
                counts[cat] += 1
                tiles.append(f'<button type="button" class="tile is-video" data-cat="{cat}" data-full="assets/video/full/{rid}.mp4" '
                             f'data-title="{a(titulo)}" data-cap="{a(cap)}" data-catname="{a(CAT_NOME[cat])}" data-ig="https://www.instagram.com/reel/{rid}/">'
                             f'<img src="assets/img/reels/{rid}.jpg" alt="{a(titulo)}" loading="lazy" width="720" height="1280">'
                             f'<span class="cap"><span class="label">{CAT_NOME[cat]}</span>{titulo}</span></button>')
        if fs:
            fid, cat, titulo, cap = fs.pop(0)
            counts[cat] += 1
            tiles.append(f'<button type="button" class="tile" data-cat="{cat}" data-img="assets/img/fotos/{fid}.jpg" data-title="{a(titulo)}: {a(cap)}">'
                         f'<img src="assets/img/fotos/{fid}.jpg" alt="{a(titulo)}: {a(cap)}" loading="lazy">'
                         f'<span class="cap"><span class="label">{CAT_NOME[cat]}</span>{titulo}</span></button>')
    total = sum(counts.values())
    btns = f'<button type="button" aria-pressed="true" data-f="todas">Todos<sup>{total}</sup></button>' + "".join(
        f'<button type="button" aria-pressed="false" data-f="{c}">{n}<sup>{counts[c]}</sup></button>' for c, n in CATS)
    return f'<div class="filters" role="group" aria-label="Filtrar trabalhos">{btns}</div><div class="mosaic" data-mosaic>{"".join(tiles)}</div>'


def servicos_lista():
    rows = []
    for i, s in enumerate(SERVICOS, 1):
        tags = "".join(f"<span>{t}</span>" for t in s["tags"])
        rows.append(f'<a class="svc" href="servicos.html#{s["id"]}" data-peek="assets/{s["img"]}" data-reveal>'
                    f'<span class="n">0{i}</span><h3>{s["nome"]}</h3><div><p>{s["curto"]}</p><div class="svc-tags">{tags}</div></div>'
                    f'<span class="go">{ARROW}</span></a>')
    return f'<div class="svc-list">{"".join(rows)}</div><div class="svc-peek" aria-hidden="true"><img alt=""></div>'


def servicos_cards():
    cards = []
    for i, s in enumerate(SERVICOS):
        itens = "".join(f"<li>{x}</li>" for x in s["itens"])
        cards.append(f'<article class="card" id="{s["id"]}" data-reveal style="--rd:{(i % 3) * .08:.2f}s">'
                     f'<div class="card-media"><img src="assets/{s["img"]}" alt="{a(s["nome"])}" loading="lazy"></div>'
                     f'<div class="card-body"><span class="label">0{i + 1} · Serviço</span><h3>{s["nome"]}</h3><p>{s["texto"]}</p><ul>{itens}</ul>'
                     f'<div class="card-cta"><a class="btn btn-wine btn-sm" href="agendamento.html?servico={quote(s["nome"])}">Agendar {ARROW}</a></div></div></article>')
    return f'<div class="cards">{"".join(cards)}</div>'


def passos():
    return '<div class="steps">' + "".join(
        f'<div class="step" data-reveal style="--rd:{i * .12:.2f}s"><b>0{i + 1}</b><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(PASSOS)) + "</div>"


def cta_bg():
    imgs = [f"img/reels/{r}.jpg" for r in DESTAQUE[:10]] + [f"img/fotos/{f[0]}.jpg" for f in FOTOS[:5]]
    cols = []
    for c in range(5):
        col = imgs[c::5] * 2
        cols.append("<div>" + "".join(f'<img src="assets/{s}" alt="" loading="lazy">' for s in col) + "</div>")
    return f'<div class="cta-bg" aria-hidden="true">{"".join(cols)}</div>'


def form():
    chips = "".join(f'<label class="chip"><input type="checkbox" name="servico" value="{s}"><span>{s}</span></label>' for s in FORM_SERVICOS)
    per = "".join(f'<label class="chip"><input type="radio" name="periodo" value="{p}"><span>{p}</span></label>' for p in ("Manhã", "Tarde", "Noite", "Tanto faz"))
    return f"""<form class="form" data-wa-form data-wa="{PERFIL['wa']}" novalidate>
  <div class="row">
    <label data-field="nome"><span>Seu nome <b>*</b></span><input name="nome" autocomplete="name" placeholder="Como podemos te chamar?" required><em class="err">Diga o seu nome.</em></label>
    <label data-field="idade"><span>Idade <b>*</b></span><input name="idade" type="number" inputmode="numeric" min="1" max="120" placeholder="Ex.: 32" required><em class="err">Informe a idade.</em></label>
  </div>
  <fieldset data-field="servico">
    <legend>Serviço desejado <b>*</b></legend>
    <div class="chips">{chips}</div>
    <em class="err">Escolha pelo menos um serviço.</em>
  </fieldset>
  <div class="row r3">
    <label data-field="data"><span>Data sugerida <b>*</b></span><input name="data" type="date" required><em class="err">Escolha uma data.</em></label>
    <label><span>Horário</span><input name="hora" type="time" step="900"></label>
    <label><span>Pessoas</span><input name="pessoas" type="number" inputmode="numeric" min="1" max="30" placeholder="1"></label>
  </div>
  <fieldset>
    <legend>Período de preferência</legend>
    <div class="chips">{per}</div>
  </fieldset>
  <label><span>Ocasião e local</span><input name="ocasiao" placeholder="Ex.: casamento na igreja, festa no Espaço X"></label>
  <label><span>Algo mais?</span><textarea name="obs" placeholder="Referências, cor do vestido, se prefere atendimento no CAZA ou no local..."></textarea></label>
  <div class="form-foot">
    <small>Ao enviar, o WhatsApp abre com tudo preenchido. A agenda é confirmada pela equipe do Cris.</small>
    <button class="btn btn-wa" type="submit">{ICONS['whatsapp']} Enviar pelo WhatsApp</button>
  </div>
</form>"""


def cur(key, current):
    return ' aria-current="page"' if key == current else ""


def brand():
    return ('<span class="brand-mark" aria-hidden="true">CR</span>'
            '<span class="brand-name">Cris Rozzini<small>Beleza assinada</small></span>')


def header(current, theme):
    links = "".join(f'<a class="nav-link" href="{h}"{cur(k, current)}>{l}</a>' for k, l, h, top in NAV if top and k != "agendamento")
    over = "".join(f'<li><a href="{h}"{cur(k, current)}>{l}</a></li>' for k, l, h, _ in NAV)
    return f"""<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<div class="progress-bar" aria-hidden="true"></div>
<div class="curtain" aria-hidden="true"><span class="curtain-word" data-w="Rozzini">Rozzini</span><span class="curtain-sub label">Maquiador e cabeleireiro · Ribeirão Preto</span></div>
<header class="site-header" data-theme="{theme}">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Cris Rozzini, página inicial">{brand()}</a>
    <nav class="nav" aria-label="Principal">
      {links}
      <a class="btn btn-sm" href="agendamento.html"{cur('agendamento', current)}>Agendar {ARROW}</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu"><span class="t">Menu</span><span class="bars"></span></button>
    </nav>
  </div>
</header>
<div class="overlay" id="menu" data-open="false" aria-hidden="true" inert>
  <ol>{over}</ol>
  <div class="overlay-foot">
    <a href="{wa()}" target="_blank" rel="noopener">{ICONS['whatsapp']} {PERFIL['wa_fone']}</a>
    <a href="{PERFIL['instagram']}" target="_blank" rel="noopener">{ICONS['instagram']} @crisrozzini</a>
  </div>
</div>
"""


def footer():
    navs = "".join(f'<li><a href="{h}">{l}</a></li>' for _, l, h, _t in NAV)
    svcs = "".join(f'<li><a href="servicos.html#{s["id"]}">{s["nome"]}</a></li>' for s in SERVICOS[:5])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <p class="label muted">Vamos marcar?</p>
        <p class="foot-lead">Conte a data e a ocasião. O Cris cuida do resto.</p>
        <div class="btn-row">
          <a class="btn" href="agendamento.html">Agendar horário {ARROW}</a>
          <a class="btn btn-ghost" href="{wa()}" target="_blank" rel="noopener">{ICONS['whatsapp']} WhatsApp</a>
        </div>
      </div>
      <div class="foot-social" aria-label="Redes sociais">
        <a href="{PERFIL['instagram']}" target="_blank" rel="noopener" aria-label="Instagram do Cris">{ICONS['instagram']}</a>
        <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICONS['whatsapp']}</a>
        <a href="{route_link()}" target="_blank" rel="noopener" aria-label="Como chegar ao CAZA">{ICONS['route']}</a>
      </div>
    </div>
    <div class="foot-grid">
      <div class="intro">
        <a class="brand" href="index.html" aria-label="Cris Rozzini">{brand()}</a>
        <p>Assinando a beleza de mulheres e homens elegantes. Noivas e eventos exclusivos em Ribeirão Preto.</p>
      </div>
      <div><h4>Navegação</h4><ul>{navs}</ul></div>
      <div><h4>Serviços</h4><ul>{svcs}</ul></div>
      <div><h4>CAZA</h4><ul>
        <li>{PERFIL['rua']}<br>{PERFIL['bairro']} · {PERFIL['cidade']}</li>
        <li><a href="{wa()}" target="_blank" rel="noopener">{PERFIL['wa_fone']}</a></li>
        <li><a href="{PERFIL['instagram_caza']}" target="_blank" rel="noopener">@cazabelezaporcrisrozzini</a></li>
        <li><a href="{route_link()}" target="_blank" rel="noopener">Como chegar</a></li>
      </ul></div>
    </div>
  </div>
  <div class="foot-word" aria-hidden="true">Cris <span>Rozzini</span></div>
  <div class="wrap">
    <div class="foot-bottom">
      <span>&copy; <span data-year>2026</span> Cris Rozzini · Ribeirão Preto, SP</span>
      <a class="dev-by" href="https://achillesmedia.com.br" target="_blank" rel="noopener">Desenvolvido por <strong>Achilles</strong></a>
      <button class="to-top" type="button" data-top>Voltar ao topo {ICONS['up']}</button>
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="Conversar no WhatsApp">{ICONS['whatsapp']}<span>Fale com o Cris</span></a>
<div class="vmodal" id="vmodal" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Vídeo" inert>
  <div class="vmodal-box">
    <video controls playsinline preload="none"></video>
    <div class="vmodal-side"><span class="label vm-cat"></span><h3 class="vm-title"></h3><p class="vm-cap"></p>
      <div class="btn-row"><a class="btn btn-sm" href="agendamento.html">Quero assim {ARROW}</a><a class="btn btn-ghost btn-sm vm-ig" href="{PERFIL['instagram']}" target="_blank" rel="noopener">{ICONS['instagram']} Ver no Instagram</a></div>
    </div>
  </div>
  <button class="vmodal-close" type="button" aria-label="Fechar vídeo">{ICONS['close']}</button>
</div>
<dialog class="lightbox" aria-label="Foto ampliada"><img src="" alt=""><p class="label"></p><button type="button" class="lb-close" aria-label="Fechar">{ICONS['close']}</button></dialog>
"""


def page_url(name):
    return f"{SITE}/" if name == "index" else f"{SITE}/{name}.html"


def page(meta, body, name):
    title = meta["title"]
    full = f"{title} | Cris Rozzini" if name != "index" else title
    url = page_url(name)
    ld = {"@context": "https://schema.org", "@type": "BeautySalon", "name": "Cris Rozzini · CAZA Beleza", "url": SITE,
          "image": f"{SITE}/assets/og-crisrozzini.jpg", "telephone": "+55 16 99786-6939",
          "address": {"@type": "PostalAddress", "streetAddress": PERFIL["rua"], "addressLocality": "Ribeirão Preto",
                      "addressRegion": "SP", "addressCountry": "BR"},
          "founder": {"@type": "Person", "name": "Cris Rozzini", "jobTitle": "Maquiador e cabeleireiro"},
          "sameAs": [PERFIL["instagram"], PERFIL["instagram_caza"]]}
    return f"""<!doctype html>
<html lang="pt-BR" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{meta['description']}">
<meta name="theme-color" content="#0c0708">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-crisrozzini.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Geist:wght@200..600&family=Geist+Mono:wght@400..500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={V}">
<script>(function(d){{d.classList.replace('no-js','js');var k='cr-intro';try{{if('{name}'==='index'&&!sessionStorage.getItem(k)){{d.classList.add('intro');sessionStorage.setItem(k,'1')}}else d.classList.add('no-intro')}}catch(e){{d.classList.add('no-intro')}}}})(document.documentElement)</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body data-page="{name}">
{header(meta.get('nav', name), meta.get('theme', 'dark'))}
<main id="conteudo">
{body.strip()}
</main>
{footer()}<script src="assets/js/main.js?v={V}" defer></script>
</body>
</html>
"""


def render(body):
    rep = {
        "{{ARROW}}": lambda: ARROW, "{{WA}}": wa, "{{WA_FONE}}": lambda: PERFIL["wa_fone"], "{{IG}}": lambda: PERFIL["instagram"],
        "{{IG_CAZA}}": lambda: PERFIL["instagram_caza"], "{{ENDERECO}}": lambda: f"{PERFIL['rua']}, {PERFIL['bairro']}, {PERFIL['cidade']}",
        "{{ROTA}}": route_link, "{{MAPA}}": map_embed, "{{GALERIA}}": galeria, "{{SERVICOS_LISTA}}": servicos_lista,
        "{{SERVICOS_CARDS}}": servicos_cards, "{{PASSOS}}": passos, "{{CTA_BG}}": cta_bg, "{{FORM}}": form,
        "{{SWATCHES}}": lambda: "".join(f'<span style="--c:{c}" title="{n}"></span>' for c, n in SWATCHES),
    }
    for k, f in rep.items():
        if k in body:
            body = body.replace(k, f())
    body = re.sub(r"\{\{RAIL:([\w-]+)\}\}", lambda m: rail(m.group(1)), body)
    body = re.sub(r"\{\{REEL:([\w-]+)\}\}", lambda m: reel(m.group(1), " solo"), body)
    return re.sub(r"\{\{ICON:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)


def main():
    urls = []
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", raw, re.S)
        if not m:
            raise SystemExit(f"{src.name}: faltando bloco <!--meta-->")
        meta = json.loads(m.group(1))
        html = page(meta, render(raw[m.end():]), src.stem)
        for bad in ("—", "–"):
            if bad in html:
                raise SystemExit(f"{src.name}: contém travessão ({bad!r}); troque por outra pontuação")
        if "{{" in html:
            raise SystemExit(f"{src.name}: marcador não substituído")
        (OUT / f"{src.stem}.html").write_text(html, encoding="utf-8")
        urls.append(page_url(src.stem))
        print("ok", src.stem + ".html")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")


if __name__ == "__main__":
    main()
