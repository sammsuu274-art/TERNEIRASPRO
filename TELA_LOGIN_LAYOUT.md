# Arquitetura CSS — Tela de Login TerneirasPro
> Última atualização: Agosto 2026  
> Este arquivo documenta a arquitetura técnica do layout, valores aprovados e a matemática por trás do posicionamento.  
> Ver também: `IMPLEMENTACAO_LOGIN.md` para contexto de design e decisões de produto.

---

## 1. CONCEITO FUNDAMENTAL

A tela de login é construída em **camadas sobrepostas**, não em colunas lado a lado.

```
┌─────────────────────────────────────────────────┐
│  .login-container  (fundo escuro #0d1f17)        │
│                                                  │
│    ┌──────────────────────────────────────┐      │
│    │  .login-right  (container da imagem) │      │
│    │                                      │      │
│    │  ┌────────────────────────────────┐  │      │
│    │  │  <img> Background.png          │  │      │
│    │  └────────────────────────────────┘  │      │
│    │                                      │      │
│    │  ┌──────────┐  (posição absoluta)    │      │
│    │  │.login-left│ = área verde 46.6%    │      │
│    │  │           │                       │      │
│    │  │ ┌───────┐ │                       │      │
│    │  │ │ CARD  │ │ centralizado          │      │
│    │  │ └───────┘ │                       │      │
│    │  └──────────┘                        │      │
│    └──────────────────────────────────────┘      │
└─────────────────────────────────────────────────┘
```

**Hierarquia de responsabilidades:**
- `.login-container` — fundo da página
- `.login-right` — dimensiona e posiciona a imagem preservando proporção
- `<img>` — a imagem em si (arte completa, não alterar)
- `.login-left` — zona que representa a área verde da imagem (position: absolute)
- `.login-card` — o formulário branco, centralizado dentro da zona verde

---

## 2. A IMAGEM Background.png

**Arquivo:** `static/img/Background.png`  
**Dimensões originais:** 1448 × 1086 px  
**Proporção (ratio):** 1448 / 1086 = **1.3333** (4:3)

### Anatomia da imagem

```
Background.png (1448px de largura)
┌─────────────────────┬─────────────────────────────┐
│                     │                             │
│   ÁREA VERDE        │   ÁREA FOTOGRÁFICA          │
│   ESCURA            │   (terneiras + grama)        │
│                     │                             │
│   0px → 675px       │   675px → 1448px            │
│   46.6% da imagem   │   53.4% da imagem           │
│                     │                             │
│   Contém:           │   Contém:                   │
│   - fundo verde     │   - fotografia rural        │
│   - espaço para o   │   - texto "Tecnologia       │
│     formulário      │     e cuidado..."           │
│                     │   - ícones de benefícios    │
└─────────────────────┴─────────────────────────────┘
                      ↑
                   x = 675px
               (medido pixel a pixel)
```

### Como foi medida a área verde

```python
# Medição via PIL/Pillow (executada em 2026)
from PIL import Image
img = Image.open('static/img/Background.png').convert('RGB')
# Escaneando linha central (y=543), pixel por pixel:
# x=670: RGB(28, 63, 29)  ← ainda verde escuro
# x=675: RGB(29, 63, 30)  ← último pixel verde
# x=680: RGB(129, 105, 28) ← transição para foto
# Resultado: área verde termina em x = 675px
```

### Conteúdo embutido na imagem (NÃO recriar em HTML)

A imagem já contém visualmente:
- Fundo verde escuro com gradiente sutil
- Texto "TECNOLOGIA E CUIDADO PARA UMA CRIAÇÃO DE SUCESSO."
- Texto "Gestão completa e profissional para sua propriedade"
- 3 ícones de benefícios (Bem-estar Animal, Monitoramento, Resultados)

**Nunca adicionar estes elementos como HTML por cima da imagem.**

---

## 3. CONTAINER PRINCIPAL — .login-container

```css
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    background: #0d1f17;   /* verde escuro neutro — não preto puro */
    position: relative;
}
```

**Por que `#0d1f17` e não `#000000`:**  
O preto puro (`#000000`) criava contraste excessivo ao redor da imagem, parecendo uma "foto flutuando em preto". O verde escuro complementa a arte de forma mais natural.

**Por que `overflow` não está aqui:**  
O overflow é `hidden` no `html, body` diretamente.

---

## 4. CONTAINER DA IMAGEM — .login-right

```css
.login-right {
    position: relative;
    aspect-ratio: 1448 / 1086;   /* proporção real da Background.png */
    max-height: 94vh;            /* não ultrapassar a viewport */
    max-width: 100%;
    width: auto;
    height: auto;
    flex-shrink: 0;
}
```

### Por que aspect-ratio é a chave desta arquitetura

Antes desta abordagem, usava-se `height: 90vh` fixo, o que causava problemas:
- O container tinha dimensão diferente da imagem renderizada
- Percentuais de `.login-left` eram relativos ao container, não à imagem
- O card podia invadir a área fotográfica em certas resoluções

Com `aspect-ratio: 1448/1086`:
- O container tem **exatamente** o mesmo tamanho da imagem renderizada
- Qualquer `width: X%` em elementos filhos é percentual da imagem real
- A matemática de posicionamento fecha em qualquer resolução

### Dimensões renderizadas por resolução

| Viewport | Altura usada (94vh) | Largura calculada | Preto visível |
|---|---|---|---|
| 1366×768 | 722px | 963px | 201px total (laterais) |
| 1440×900 | 846px | 1128px | 312px total |
| 1920×1080 | 1015px | 1353px | 567px total |

---

## 5. IMAGEM — .login-right-image

```css
.login-right-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
    border-radius: 14px;
}
```

**Por que `object-fit: contain` (não `cover`):**  
`cover` corta a imagem para preencher o container. Como os textos e ícones estão embutidos na arte, qualquer corte esconde informação. `contain` é seguro porque o container já tem a proporção exata da imagem — não sobra espaço em branco.

**Por que não usar como `background-image`:**  
`background-image` não permite `position: absolute` de filhos em relação à imagem. A tag `<img>` dentro do container possibilita o aninhamento de `.login-left`.

---

## 6. ZONA DA ÁREA VERDE — .login-left

```css
.login-left {
    position: absolute;
    left: 0;
    top: 0;
    width: 46.6%;     /* 675px / 1448px = 46.6% da imagem */
    height: 100%;

    display: flex;
    align-items: center;     /* centraliza verticalmente */
    justify-content: center; /* centraliza horizontalmente */

    box-sizing: border-box;
    padding: 16px;           /* margem de segurança interna */

    z-index: 10;
}
```

### Por que width: 46.6% é a decisão correta

Esta é a regra central de toda a arquitetura:

```
.login-left representa EXPLICITAMENTE a área verde da imagem.
Não é uma aproximação. É a medida real.
```

Como `.login-right` tem o mesmo tamanho da imagem renderizada, `width: 46.6%` de `.login-right` = `46.6%` da imagem = exatamente a área verde.

`justify-content: center` garante que o card fica **matematicamente centralizado** dentro da área verde, com margens iguais dos dois lados.

### Verificação matemática por resolução

| Viewport | Img renderizada | Área verde (46.6%) | Card (320px) | Margem cada lado |
|---|---|---|---|---|
| 1366×768 | ~963px | ~449px | 320px (−padding) | ~47px |
| 1440×900 | ~1128px | ~526px | 320px (−padding) | ~85px |
| 1920×1080 | ~1353px | ~631px | 320px (−padding) | ~138px |

O `padding: 16px` reduz o espaço disponível para o card em 32px (16 de cada lado), garantindo margem mínima da borda da imagem.

---

## 7. CARD DO FORMULÁRIO — .login-card

```css
.login-card {
    width: min(320px, 100%);
    box-sizing: border-box;
    padding: 32px 28px 28px 28px;
    background: white;
    border-radius: 24px;
    box-shadow:
        0 2px 4px rgba(0, 0, 0, 0.06),
        0 16px 40px rgba(0, 0, 0, 0.18);
    display: flex;
    flex-direction: column;
    gap: 0;
    animation: fadeInUp 0.5s ease-out;
}
```

**Por que `min(320px, 100%)`:**  
- `320px` é o tamanho fixo ideal para o card
- `100%` garante que nunca ultrapasse o `.login-left` container
- Em telas muito pequenas (< 320px de área verde), o card encolhe proporcionalmente

**Separação de responsabilidades:**
- `.login-left` controla POSIÇÃO (onde o card fica)
- `.login-card` controla TAMANHO (quanto o card ocupa)

---

## 8. BRANDING — .brand-section

```css
.brand-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;              /* sem espaço extra entre logo e subtítulo */
    margin-bottom: 16px; /* espaço entre branding e formulário */
}

.login-card .brand-logo {
    width: auto;
    max-width: 200px;    /* APROVADO — não alterar */
    height: auto;
}

.brand-subtitle {
    font-size: 0.775rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.3px;
    /* NÃO usar margin-top negativo */
}
```

**Nota sobre espaço entre logo e subtítulo:**  
O arquivo `logo-terneiraspro.png` tem espaço em branco interno abaixo do texto "TerneirasPro". O `gap: 0` elimina espaço extra do flexbox. Se ainda houver espaço visível, é interno à imagem do logo — não corrigir com `margin-top` negativo.

---

## 9. CAMPOS DO FORMULÁRIO

```css
.form-group { margin-bottom: 12px; }

.form-control {
    width: 100%;
    padding: 10px 14px 10px 40px;  /* padding-left para o ícone */
    height: 44px;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #0f172a;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
    border-color: #16a34a;
    box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}

/* Ícone à esquerda do campo */
.input-icon {
    position: absolute;
    left: 13px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 1rem;
    pointer-events: none;
}
```

---

## 10. HIERARQUIA DE AÇÕES DO FORMULÁRIO

```
.form-options          margin-top: 4px, margin-bottom: 14px
  └── .form-check      checkbox "Lembrar meu acesso" — SOZINHO na linha

.btn-login             altura 44px, verde #16a34a, uppercase
                       AÇÃO PRINCIPAL

.forgot-wrapper        margin-top: 12px, justify-content: center
  └── .forgot-password AÇÃO SECUNDÁRIA: font menor (0.775rem), weight 500
                       NÃO ao lado do checkbox
```

**Regra de hierarquia visual:**
1. Campos → foco funcional
2. Checkbox → controle de sessão
3. Botão ENTRAR → CTA principal, máximo destaque
4. Esqueceu sua senha? → ação secundária, fonte menor, sem competir com o botão

---

## 11. RESPONSIVIDADE

### Breakpoint 768px — mobile

```css
@media (max-width: 768px) {
    html, body { overflow: auto; }          /* permite scroll no mobile */

    .login-container {
        background: #0a2d1f;               /* verde escuro da marca */
        min-height: 100vh;
        height: auto;
        padding: 40px 20px;
    }

    .login-right {
        aspect-ratio: unset;               /* remove proporção da imagem */
        width: 100%;
        height: auto;
    }

    .login-right-image { display: none; }  /* oculta a imagem */

    .login-left {
        position: relative;                /* sai do fluxo absoluto */
        left: auto; top: auto;
        width: 100%;
        max-width: 100%;
        display: flex;
        justify-content: center;
    }

    .login-card {
        width: 100%;
        max-width: 400px;
        padding: 36px 28px 40px 28px;
    }
}
```

### Breakpoint 480px — extra small

```css
@media (max-width: 480px) {
    .login-container { padding: 24px 16px; }
    .login-card {
        padding: 28px 22px 32px 22px;
        border-radius: 18px;
    }
    .login-card .brand-logo { max-width: 180px; }
}
```

---

## 12. VALORES APROVADOS — NÃO ALTERAR SEM JUSTIFICATIVA

| Propriedade | Valor aprovado | Motivo |
|---|---|---|
| `Background.png` dimensões | 1448 × 1086 px | Imagem original |
| `aspect-ratio` | `1448 / 1086` | Proporção real da imagem |
| `max-height` da imagem | `94vh` | Espaço confortável sem cortar |
| `width` do `.login-left` | `46.6%` | Medição pixel a pixel da área verde |
| `max-width` do logo | `200px` | Proporção aprovada no card 320px |
| `width` do `.login-card` | `min(320px, 100%)` | Tamanho ideal com fallback seguro |
| `border-radius` do card | `24px` | Cantos arredondados modernos |
| `border-radius` da imagem | `14px` | Moldura da arte no fundo escuro |
| Fundo do container | `#0d1f17` | Complementa a arte (não preto puro) |
| Fundo mobile | `#0a2d1f` | Verde escuro da identidade |
| Verde principal | `#16a34a` | Botão, focus, checkbox, links |

---

## 13. ANTI-PADRÕES — O QUE NÃO FAZER

Padrões que já foram tentados e causaram problemas:

| Anti-padrão | Problema causado |
|---|---|
| `margin-top: -20px` no subtítulo | Hack frágil, depende do tamanho da fonte |
| `margin-left: 26px` no link | Offset arbitrário que quebra em resoluções diferentes |
| `height: 90vh` no `.login-right` | Container maior que a imagem, percentuais filhos errados |
| `object-fit: cover` na imagem | Corta textos e ícones embutidos na arte |
| `background-image` no `.login-right` | Impede aninhamento correto do card |
| `position: fixed` no container | Quebra o scroll e causa problemas com a barra do browser |
| `overflow: hidden` no container | Pode cortar o card em viewports pequenas |
| `left: 3%` no `.login-left` | Não garante centralização — é offset, não posição |
| `width: 41%` no `.login-card` | Mistura responsabilidade de posição com tamanho |
| `max-width: 44%` no `.login-left` | Limite, não posição — não garante centralização |
| Recriar título/ícones em HTML | Duplicação do conteúdo da imagem |
| Overlay escuro sobre a imagem | Esconde o conteúdo visual da arte |
| `transform: translateY(-50%)` + `top: 50%` | Frágil quando card tem altura variável |

---

## 14. FLUXO DE DIAGNÓSTICO

Se o card aparecer fora da área verde, verificar nesta ordem:

1. `.login-right` tem `aspect-ratio: 1448 / 1086`? → Se não, o container tem tamanho errado
2. `.login-right-image` tem `width: 100%; height: 100%`? → Se não, a imagem não preenche o container
3. `.login-left` tem `width: 46.6%` e `position: absolute; left: 0; top: 0`? → Se não, a zona verde está errada
4. `.login-left` tem `justify-content: center`? → Se não, o card não está centralizado na zona
5. `.login-card` tem `width: min(320px, 100%)`? → Se não, pode estar maior que a zona

Se a imagem estiver cortada (título ou ícones não aparecem):
- `object-fit: contain` na imagem? Se `cover`, trocar para `contain`

---

## 15. CHECKLIST ANTES DE QUALQUER ALTERAÇÃO NO LAYOUT

```
[ ] Verificou as dimensões reais da Background.png? (1448 × 1086)
[ ] O aspect-ratio do .login-right bate com a proporção da imagem?
[ ] O width do .login-left é 46.6% (medida real da área verde)?
[ ] O card está centralizado via justify-content: center, não via left arbitrário?
[ ] A largura do card é separada da lógica de posicionamento?
[ ] Nenhum margin negativo foi adicionado?
[ ] A imagem continua com object-fit: contain?
[ ] O mobile continua funcionando (imagem oculta, card centralizado)?
[ ] Não há texto duplicado em relação ao conteúdo da imagem?
```
