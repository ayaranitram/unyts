# Version History

## Recent Releases

### v0.10.1 (2026-02-27) - Current Release ⭐
**Major Performance & Feature Release**

- 200× faster imports (14.5s → 0.08s)
- 60% faster database builds (40s → 16-17s)
- 78% faster rebuilds with caching (40s → 9s)
- Lazy module loading (PEP 562)
- Enhanced search with Lean BFS
- Alias conflict detection system
- Network export to DataFrame
- GUI improvements
- Comprehensive test suite
- Full backward compatibility

**Key Stats**: 38 module updates, 9+ test modules, 6 cache types, Python 3.7-3.11 support

[Full Details](CHANGELOG.md#0101---2026-02-27) | [Release Notes](RELEASE_NOTES.md)

---

### v0.10.0 (2026-02-25)
**Performance & Optimization Release**

- Initial performance optimizations
- GUI enhancements (v0.4.8)
- Database improvements (v0.8.1)
- Enhanced converter (v0.8.10)
- Updated parameters system (v0.6.13)

---

### v0.9.x Series (Pre-optimization)

Series focused on feature development and stability improvements before the major performance overhaul in v0.10.0.

#### v0.9.15 and Earlier
- Core conversion functionality
- Basic GUI implementation
- Unit class system
- Graph-based conversion network
- BFS search algorithm
- Configuration system
- Cache support
- SI and Imperial unit systems
- Compound unit support

---

## Module Version Matrix (v0.10.1)

| Module | Version | Release Date |
|--------|---------|--------------|
| **Core Package** | 0.10.1 | 2026-02-27 |
| converter.py | 0.8.10 | 2026-02-25 |
| database.py | 0.8.1 | 2026-03-05 |
| dictionaries.py | 0.6.0 | 2026-02-27 |
| parameters.py | 0.6.13 | 2026-02-25 |
| searches.py | 0.6.7 | 2026-02-25 |
| unit_class.py | 0.6.7 | 2026-02-24 |
| operations.py | 0.5.4 | 2024-05-21 |
| network.py | 0.4.25 | 2026-02-25 |
| gui.py | 0.4.8 | 2026-02-25 |
| errors.py | 0.4.9 | 2025-05-04 |
| __main__.py | 0.1.1 | 2024-03-19 |
| Empty.py | 0.1.0 | 2025-05-04 |
| unitary.py | 0.0.1 | 2023-01-28 |

### Unit Definitions

| Module | Version | Release Date |
|--------|---------|--------------|
| ratios.py | 0.5.32 | 2025-03-20 |
| custom.py | 0.5.32 | 2026-02-25 |
| unitless.py | 0.5.31 | 2025-03-20 |
| time.py | 0.5.31 | 2025-03-20 |
| temperature.py | 0.5.31 | 2025-03-20 |
| rates.py | 0.5.31 | 2025-03-20 |
| mass.py | 0.5.31 | 2025-03-20 |
| geometry.py | 0.5.31 | 2025-03-20 |
| force.py | 0.5.31 | 2025-03-20 |
| energy.py | 0.5.31 | 2025-03-20 |
| date.py | 0.5.31 | 2025-03-23 |
| define.py | 0.5.30 | 2023-07-24 |
| data.py | 0.5.30 | 2023-07-24 |
| def_conversions.py | 0.1.2 | 2025-06-01 |
| def_prefixes.py | 0.1.1 | 2025-03-24 |

### Helper Modules

| Module | Version | Release Date |
|--------|---------|--------------|
| unit_string_tools.py | 0.5.2 | 2023-01-18 |
| multi_split.py | 0.5.3 | 2026-02-27 |
| common_classes.py | 0.5.7 | 2023-12-30 |
| caster.py | 0.4.10 | 2023-12-30 |
| is_unit.py | 0.4.9 | 2023-01-18 |
| is_number.py | 0.4.7 | 2022-12-29 |
| logger.py | 0.1.1 | 2025-06-15 |
| timer.py | 0.1.0 | 2026-02-22 |
| _parallel_helpers.py | 0.1.0 | 2026-02-25 |

---

## Release Cadence

| Period | Releases | Focus |
|--------|----------|-------|
| 2026-02-25 to 2026-03-05 | v0.10.0 - v0.10.1 | Performance optimization |
| Pre-2026 | v0.0.x - v0.9.15 | Feature development |

---

## Upgrade Path

### From v0.9.15 to v0.10.1
✅ **Direct upgrade** - Fully backward compatible

```bash
pip install --upgrade unyts
```

Optional: Clear old caches for optimal performance:
```python
from unyts import delete_cache
delete_cache()
```

### From Earlier Versions
✅ **Direct upgrade** - All versions 0.x.x are backward compatible

---

## Python Version Support

| unyts Version | Python Versions |
|---------------|-----------------|
| 0.10.1 | 3.7, 3.8, 3.9, 3.10, 3.11 |
| 0.10.0 | 3.7, 3.8, 3.9, 3.10, 3.11 |
| 0.9.x | 3.7, 3.8, 3.9, 3.10 |

---

## License

All versions released under MIT License.

---

## Links

- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Release Notes**: [RELEASE_NOTES.md](RELEASE_NOTES.md)
- **GitHub**: https://github.com/ayaranitram/unyts
- **PyPI**: https://pypi.org/project/unyts/
