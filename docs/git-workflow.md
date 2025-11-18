\# Git Workflow - DevSpell



\## Estrategia de Ramas



\### Ramas Principales



main (producción)

↑

develop (integración)

↑

feature/\* (desarrollo)



\### Tipos de Ramas



| Tipo | Nomenclatura | Propósito | Se crea desde |

|------|-------------|-----------|---------------|

| \*\*feature\*\* | `feature/nombre-descriptivo` | Nueva funcionalidad | `develop` |

| \*\*fix\*\* | `fix/nombre-del-bug` | Corrección de bugs | `develop` |

| \*\*docs\*\* | `docs/nombre-documento` | Solo documentación | `develop` |

| \*\*refactor\*\* | `refactor/que-se-refactoriza` | Mejora de código sin cambiar funcionalidad | `develop` |



---



\## Flujo de Trabajo



\### 1. Crear Nueva Feature

```bash





