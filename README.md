### Setup
```
# create venv
uv venv

# activate venv
.\.venv\Scripts\activate   

# Install main dependencies
uv add psutil pyyaml typing-extensions

# Install development dependencies
uv add --dev ruff black mypy pytest pytest-cov
```

### Run ruff
```
ruff check . --config pyproject.toml
```

### Run project 
```
python Main.py
```

### Open the html file data/dashboard.html to see the results

## Buenas Prácticas de Diseño

### Alta Cohesión

El proyecto implementa **alta cohesión** agrupando funcionalidades relacionadas en módulos específicos:

#### Ejemplos de Alta Cohesión:

1. **File1.py - ModelInfo y ModelValidator**
   - Todas las funciones están relacionadas con información y validación de modelos
   - `ModelInfo` encapsula atributos del modelo y métodos de acceso
   - `ModelValidator` se enfoca únicamente en validación de modelos
   ```python
   # Alta cohesión: todas las funciones relacionadas con validación
   class ModelValidator:
       def validate_model(self, model)
       def _validate_model_name(self, name)
       def _validate_task_type(self, task_type)
       def _validate_library(self, library)
   ```

2. **File3.py - ConfigManager y StorageManager**
   - `ConfigManager`: solo maneja configuración (cargar, guardar, validar)
   - `StorageManager`: solo maneja persistencia de datos
   ```python
   # Alta cohesión: ConfigManager solo maneja configuración
   class ConfigManager:
       def load_config(self)
       def save_config(self) 
       def get_setting(self)
       def update_setting(self)
       def validate_config(self)
   ```

3. **File4.py - PerformanceMonitor**
   - Agrupa todas las funciones relacionadas con monitoreo de rendimiento
   - Separación clara entre recolección y análisis de métricas

### Bajo Acoplamiento

El proyecto minimiza dependencias entre módulos mediante interfaces bien definidas:

#### Ejemplos de Bajo Acoplamiento:

1. **Inyección de Dependencias**
   ```python
   # File3.py - DataPersistence
   class DataPersistence:
       def __init__(self, config_manager: ConfigManager, storage_manager: StorageManager):
           self.config = config_manager  # Recibe dependencias como parámetros
           self.storage = storage_manager
   ```

2. **Interfaces Genéricas**
   ```python
   # File2.py - ModelManager trabaja con cualquier ModelInfo
   class ModelManager:
       def add_model(self, model: ModelInfo) -> bool  # No depende de implementación específica
       def get_models_by_task(self, task_type: str)   # Interfaz genérica
   ```

3. **Separación de Responsabilidades**
   - `ModelDownloader` no conoce la estructura interna de `ModelInfo`
   - `WebInterface` no depende de implementaciones específicas de modelos
   - `DashboardRenderer` recibe datos preparados, no accede directamente a modelos

4. **Abstracción en Storage**
   ```python
   # File3.py - StorageManager usa backends intercambiables
   def save_data(self, data: Any, filename: str, format: str = "json"):
       backend = self.storage_backends.get(format, self._json_backend)
       return backend("save", file_path, data)
   ```

### Beneficios Obtenidos:

- **Mantenibilidad**: Cambios en un módulo no afectan otros
- **Testabilidad**: Cada clase puede ser probada independientemente
- **Reutilización**: Componentes pueden usarse en otros contextos
- **Escalabilidad**: Fácil agregar nuevas funcionalidades
- **Legibilidad**: Código organizado y fácil de entender
