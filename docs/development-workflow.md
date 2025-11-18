# Workflow de Desarrollo

## Para cada feature:

1. **Planificar** (Claude.ai web)
   - Discutir diseño
   - Crear spec en docs/

2. **Especificar** (tu PC)
   - Crear docs/feature-X.md
   - Definir inputs/outputs
   - Listar tests necesarios

3. **Generar** (Claude Code terminal)
   - `claude-code create` con contexto
   - Verificar archivos generados

4. **Refinar** (VS Code + Claude)
   - Ajustes manuales si necesario
   - Claude inline para dudas

5. **Revisar** (Claude Code terminal)
   - `claude-code review`
   - Corregir issues

6. **Testear** (terminal)
   - Ejecutar pytest
   - Validar coverage

7. **Commit** (Git)
   - Commit con mensaje claro
   - Push a GitHub

8. **Documentar** (Claude.ai)
   - Actualizar Knowledge Base
   - Registrar decisiones
```


---

## Git Workflow (IMPORTANTE)

⚠️ **NUNCA trabajar directamente en main o develop**

### Para cada feature/sprint:

1. **Crear rama desde develop**
```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nombre-descriptivo
```

2. **Trabajar normalmente**
   - Crear archivos
   - Hacer commits incrementales
   - Push a la rama

3. **Pull Request en GitHub**
   - Base: develop
   - Compare: tu feature branch
   - Descripción completa
   - Merge después de review

4. **Limpiar después del merge**
```bash
   git checkout develop
   git pull origin develop
   git branch -d feature/nombre-descriptivo
```

Ver detalles completos en: `docs/git-workflow.md`


