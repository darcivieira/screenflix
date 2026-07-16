---
name: new-module
description: Cria o esqueleto de um novo módulo de negócio seguindo a Clean Architecture do ScreenFlix (domain, application, infrastructure, presentation).
invocation: manual
---

Dado o nome de um módulo `<nome>`, crie em `src/screenflix/modules/<nome>/` as pastas e
`__init__.py` replicando o padrão de `modules/catalog/`:

- `domain/entities/`
- `application/{schemas,services,use_cases}/`
- `infrastructure/repositories/`
- `adapters/`  (apenas se houver integração externa)
- `presentation/api/v1/endpoints/`

Regras:
- Respeite a regra de dependência: presentation → application → domain; infrastructure/adapters
  dependem de domain e core, nunca de presentation.
- Registre o router em `presentation/api/v1/router.py` e inclua-o no app com o prefixo `/api/v1`.
- Não implemente lógica de negócio — só o esqueleto tipado, pronto para receber os casos de uso.
- Todo componente novo precisa de testes (caminho feliz, validação, erro) no mesmo change set.
