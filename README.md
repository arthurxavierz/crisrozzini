# Cris Rozzini · site

Site do Cris Rozzini, maquiador e cabeleireiro em Ribeirão Preto (CAZA Beleza por Cris Rozzini), no molde dos sites da MC Miaki e do Eficaz: várias páginas, gerador em Python, sem framework.

- No ar: https://crisrozzini.achillesmedia.com.br (GitHub → Netlify → CNAME na Cloudflare, DNS only)
- Instagram: https://www.instagram.com/crisrozzini/ · Salão: https://www.instagram.com/cazabelezaporcrisrozzini/

## Como editar
1. Dados (WhatsApp, endereço, reels, fotos, serviços, passos) ficam no topo de `src/build.py`.
2. Textos de cada página ficam em `src/pages/*.html`.
3. Rode `python src/build.py`. Ele gera `dist/*.html` e o `sitemap.xml`, e recusa travessão no texto.
4. Mudou CSS ou JS (`dist/assets/css/style.css`, `dist/assets/js/main.js`)? Suba o `V` no `build.py` e rode de novo.
5. Push na `main` publica no Netlify.

Preview local: config `crisrozzini` (porta 5300) no `.claude/launch.json` da pasta da agência.

## Páginas
Início (hero com 3 reels, glitter e pincelada; vitrine; serviços; passos), Sobre (história desde 2010, visagismo, podcast, trajetória, propósito), Trabalhos (vitrine de noivas e galeria com filtro), Serviços (6 cartões, cada um leva ao agendamento já marcado), O CAZA (espaço, prêmio, bastidores, mapa), Agendamento (formulário que monta a mensagem no WhatsApp com prévia ao vivo) e Contato.

## Identidade
Vinho `#5c0f26`/`#7e1a37`, rosa `#e49ab0`, blush `#f4d3dc`, branco `#fffafb` e preto `#0c0708`. Anton em todos os títulos, Geist no texto, Geist Mono nos rótulos.

## Mídia
- Tudo vem do Instagram do Cris (originais em `_raw/`, fora do git). `python tools/media.py` recorta e comprime: colunas do hero, montagem vertical do celular, prévias mudas de 6 s, reels completos com som (modal), capas, quadros parados e fotos.
- A lista de reels e fotos usada no site fica em `REELS` e `FOTOS` no `build.py`; os cortes ficam em `tools/media.py`.

## Validar com o cliente
- [ ] WhatsApp: usei o do salão (16) 99786-6939, que é o link da bio do CAZA. Confirmar se o agendamento vai para esse número ou para um pessoal.
- [ ] Horários de atendimento (não estão públicos; o site diz "atendimento com hora marcada").
- [ ] Autorização das clientes que aparecem nos vídeos e fotos (todas publicadas no perfil dele, mas vale confirmar).
- [ ] Ano do reconhecimento "Top 53 salões" e nome da feira.
- [ ] Logo do CAZA em vetor, se ele quiser no lugar do monograma "CR".
