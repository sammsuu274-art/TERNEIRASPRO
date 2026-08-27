# Implementação da Tela de Login — TerneirasPro
> Última atualização: Agosto 2026  
> Para detalhes técnicos de CSS e layout, ver `TELA_LOGIN_LAYOUT.md`

---

## 1. VISÃO GERAL

A tela de login do TerneirasPro é uma página **standalone** (não herda `base.html`) com design exclusivo baseado em sobreposição de camadas:

- **Fundo:** `Background.png` — arte completa com área verde escura + fotografia de terneiras
- **Card:** formulário branco sobreposto à área verde da imagem
- **Conceito:** a imagem é tratada como uma moldura pronta; o HTML apenas adiciona o formulário por cima

**Arquivo:** `templates/accounts/login.html`  
**URL:** `/accounts/login/`  
**View:** `accounts/views.py → login_view()`

---

## 2. ARQUIVOS ENVOLVIDOS

| Arquivo | Função |
|---|---|
| `templates/accounts/login.html` | Template completo — HTML + CSS inline + JS |
| `accounts/views.py` | Views de autenticação |
| `accounts/urls.py` | Rotas com namespace `accounts` |
| `gestao_terneiras/settings.py` | `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` |
| `static/img/Background.png` | Arte da tela — **não alterar** |
| `static/img/logo-terneiraspro.png` | Logo — **não alterar** |

---

## 3. CONFIGURAÇÕES DJANGO (settings.py)

```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

---

## 4. URLs (accounts/urls.py)

```python
app_name = 'accounts'

urlpatterns = [
    path('login/',        views.login_view,        name='login'),
    path('logout/',       views.logout_view,        name='logout'),
    path('dashboard/',    views.dashboard_view,     name='dashboard'),
    path('perfil/',       views.perfil_view,        name='perfil'),
    path('api/check-user/', views.check_user_status, name='check_user'),
]
```

**Uso nos templates:** `{% url 'accounts:login' %}`, `{% url 'accounts:logout' %}`

---

## 5. VIEWS (accounts/views.py)

### login_view
```python
@never_cache
@csrf_protect
def login_view(request):
```
- Redireciona para `dashboard` se já autenticado
- Lê `username`, `password`, `remember_me` do POST
- `remember_me=True` → sessão de 2 semanas (`set_expiry(1209600)`)
- `remember_me=False` → sessão expira ao fechar navegador (`set_expiry(0)`)
- Suporta `?next=` para redirecionamento pós-login
- Mensagens via `django.contrib.messages`

### logout_view
```python
@login_required
def logout_view(request):
```
- Requer autenticação
- Redireciona para `accounts:login` após logout

### dashboard_view / perfil_view
```python
@login_required
def dashboard_view(request):
def perfil_view(request):
```
- Protegidas por `@login_required`

### check_user_status
- Endpoint JSON (POST) para validação AJAX
- Retorna `exists`, `is_active`, `full_name`

---

## 6. ESTRUTURA DO TEMPLATE

O template é dividido em três partes:

### 6.1 Head — dependências externas
```html
<!-- Google Fonts Inter (400/500/600/700) -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">

<!-- Bootstrap Icons 1.11.3 (apenas para ícones nos campos) -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
```

> **Atenção:** Bootstrap CSS **não é carregado** nesta página. Todo estilo é customizado.

### 6.2 Estrutura HTML do body

```
.login-container
  └── .login-right                    ← container da imagem
        ├── <img class="login-right-image">  ← Background.png
        └── .login-left               ← zona da área verde (position: absolute)
              └── .login-card         ← card branco do formulário
                    ├── .brand-section
                    │     ├── .brand-logo → <img logo>
                    │     └── .brand-subtitle → "Gestão de Cria e Recria"
                    ├── {% if messages %} alertas {% endif %}
                    ├── <form method="post">
                    │     ├── {% csrf_token %}
                    │     ├── .form-group (usuário)
                    │     ├── .form-group (senha + toggle)
                    │     ├── .form-options (checkbox lembrar)
                    │     ├── <button class="btn-login"> ENTRAR
                    │     └── .forgot-wrapper → link "Esqueceu sua senha?"
                    └── </form>
```

### 6.3 Hierarquia visual dentro do card

```
[ LOGO TERNEIRASPRO ]
  Gestão de Cria e Recria

  USUÁRIO
  [campo]

  SENHA
  [campo 👁]

  ☐ Lembrar meu acesso

  [ ENTRAR ]

      Esqueceu sua senha?
```

### 6.4 JavaScript inline
- Toggle show/hide senha (troca `type=password` ↔ `type=text`, alterna ícone `bi-eye` / `bi-eye-slash`)
- Validação básica de campos vazios antes do submit
- Prevenção de zoom em iOS (font-size: 16px no focus)

---

## 7. CAMPOS DO FORMULÁRIO

| Campo | name | type | Observações |
|---|---|---|---|
| Usuário | `username` | text | `autofocus`, `autocomplete="username"` |
| Senha | `password` | password | toggle de visibilidade |
| Lembrar acesso | `remember_me` | checkbox | `on` = sessão 2 semanas |
| CSRF | — | hidden | `{% csrf_token %}` |

---

## 8. MENSAGENS DO DJANGO

O template exibe `{% if messages %}` com as seguintes classes Bootstrap-compatíveis:

| Tag Django | Classe CSS | Aparência |
|---|---|---|
| `error` | `alert-danger` | fundo vermelho claro, borda esquerda vermelha |
| `success` | `alert-success` | fundo verde claro, borda esquerda verde |
| `info` | `alert-info` | fundo azul claro, borda esquerda azul |

---

## 9. DESIGN — DECISÕES APROVADAS

### O que está aprovado e não deve ser alterado

| Elemento | Estado aprovado |
|---|---|
| Background.png | Imagem única com arte completa — não recriar elementos em HTML |
| Estrutura de sobreposição | `.login-left` dentro de `.login-right` |
| Tamanho do logo | `max-width: 200px` |
| Posição do card | Centralizado na área verde (via `width: 46.6%` + `justify-content: center`) |
| Hierarquia do formulário | Logo → subtítulo → campos → checkbox → botão → link |
| Posição do "Esqueceu sua senha?" | Abaixo do botão ENTRAR, centralizado |
| Fundo do container | `#0d1f17` (verde escuro neutro, não preto puro) |
| Borda da imagem | `border-radius: 14px` |

### O que NÃO fazer

- Não colocar "Esqueceu sua senha?" ao lado do checkbox
- Não recriar o título "Tecnologia e cuidado..." em HTML (está na imagem)
- Não recriar os ícones de benefícios em HTML (estão na imagem)
- Não aplicar overlay sobre a imagem (esconde conteúdo da arte)
- Não usar `margin-top` negativo para ajustar espaçamento
- Não usar `position: fixed` no container
- Não usar Bootstrap `.container` (limita largura)
- Não transformar Background.png em background-image CSS

---

## 10. RESPONSIVIDADE

### Desktop (> 768px)
- Imagem centralizada com fundo escuro ao redor
- Card sobreposto à área verde

### Mobile (≤ 768px)
```css
.login-container { background: #0a2d1f; }  /* verde escuro da marca */
.login-right-image { display: none; }       /* oculta a imagem */
.login-left {                               /* sai do absolute */
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
}
.login-card { max-width: 400px; }
```
- Imagem oculta, card centralizado sobre fundo verde escuro
- Experiência coerente com identidade da marca

### Extra small (≤ 480px)
- Padding reduzido: `24px 16px`
- Logo: `max-width: 180px`
- Border-radius menor: `18px`

---

## 11. IDENTIDADE VISUAL

| Elemento | Valor |
|---|---|
| Fundo do container | `#0d1f17` |
| Fundo mobile | `#0a2d1f` |
| Verde do botão | `#16a34a` |
| Verde hover do botão | `#15803d` |
| Verde focus dos campos | `#16a34a` |
| Verde links | `#16a34a` |
| Cor texto principal | `#0f172a` |
| Cor labels | `#1e293b` |
| Cor subtítulo | `#64748b` |
| Cor placeholder | `#94a3b8` |
| Cor checkbox marcado | `#16a34a` |
| Fonte | Inter (Google Fonts) |

---

## 12. SEGURANÇA

- `@never_cache` na view — impede que a tela de login seja cacheada
- `@csrf_protect` — proteção CSRF
- CSRF token no formulário via `{% csrf_token %}`
- Senhas nunca expostas no HTML
- `autocomplete="current-password"` no campo senha
- Validação server-side no Django Auth

---

## 13. PRÓXIMOS PASSOS (não implementados)

- [ ] Recuperação de senha (fluxo completo com email)
- [ ] Autenticação em dois fatores (2FA)
- [ ] Logs de acesso/auditoria
- [ ] Configuração HTTPS + `SESSION_COOKIE_SECURE` para produção

---

## 14. CREDENCIAIS DE DESENVOLVIMENTO

```
Usuário: admin
URL:     http://127.0.0.1:8000/accounts/login/
Servidor: source venv/bin/activate && python manage.py runserver
```
