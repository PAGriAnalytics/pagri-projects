var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.heatMap = function (props) {
    const {min, max} = props.colDef.cellRendererParams;
    const val = props.value;

    // Определяем начальный и конечный цвета
    const startColor = { r: 230, g: 220, b: 230 }; // rgba(204, 153, 255, 0.1)
    const endColor = { r: 127, g: 60, b: 141 }; // rgb(127, 60, 141)

    // Нормализуем значение val в диапазоне от 0 до 1
    const normalizedValue = (val - min) / (max - min);
    const clampedValue = Math.min(Math.max(normalizedValue, 0), 1); // Ограничиваем значение от 0 до 1

    // Интерполируем цвета
    const r = Math.round(startColor.r + (endColor.r - startColor.r) * clampedValue);
    const g = Math.round(startColor.g + (endColor.g - startColor.g) * clampedValue);
    const b = Math.round(startColor.b + (endColor.b - startColor.b) * clampedValue);

    // Определяем цвет текста в зависимости от значения
    const textColor = val > 0.6 * max ? 'white' : 'black';

    return {
        backgroundColor: 'rgb(' + [r, g, b].join(',') + ')',
        color: textColor,
    }
};