# 🎯 Simulador de Compensación Optimaxx PLUS

## Dashboard Completo de Compensación de Ventas con Modelo Bowtie

### 🚀 Características Principales

- **Control Granular del Equipo**: Especifica exactamente cuántos closers, setters, personas en banca
- **Validaciones Automáticas**: Detecta inconsistencias y sugiere mejoras
- **Modelo Bowtie (Winning by Design)**: Implementación correcta del funnel completo
- **Costos Unitarios Completos**: CPL, CPC, CPM, CPA, CAC, LTV
- **Sistema de Compensación Editable**: Ajusta todos los parámetros en tiempo real
- **Modelo Optimaxx PLUS**: Específico para seguros con pagos diferidos

### 📊 Uso

1. **Configura tu equipo** en el sidebar (números exactos)
2. **Define tu volumen de leads** y costos
3. **Ajusta las tasas de conversión** del funnel
4. **Personaliza la compensación** por rol
5. **Ve las alertas** si hay inconsistencias
6. **Analiza el P&L completo** y toma decisiones

### 🎯 Validaciones Incluidas

- Capacidad del equipo vs volumen de leads
- Ratios setter:closer óptimos
- Alertas de sobrecarga o subutilización
- Análisis LTV:CAC automático
- Sugerencias específicas de mejora

### 💰 Modelo de Compensación

Basado en el producto Optimaxx PLUS:
- Prima Mensual × 300 meses × 2.7% = Compensación Total
- 70% pago inmediato + 30% diferido (mes 18)
- Distribución interna configurable
- Bonos por velocidad y seguimiento

### 📈 Archivos Principales

- `app.py` - Dashboard principal
- `fixed_compensation_dashboard.py` - Versión corregida completa
- `optimaxx_plus_model.py` - Modelo específico de seguros
- `sales_process_integration.py` - Integración del proceso de ventas

### 🔧 Dependencias

- streamlit>=1.35.0
- numpy>=1.26.0
- pandas>=2.1.0
- plotly>=5.18.0
- scipy>=1.12.0
