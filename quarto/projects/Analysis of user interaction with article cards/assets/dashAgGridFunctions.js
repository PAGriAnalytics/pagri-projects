var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.heatMap = function (props) {
    const {min, max} = props.colDef.cellRendererParams;
    const val = props.value;

    if (val > 0) {
        g = 255;
        r = b = 255 * (1 - val / max);
    } else {
        r = 255;
        g = b = 255 * (1 - val / min);
    }

    return {
        backgroundColor: 'rgb(' + [r, g, b].join() + ')',
        color: 'black',
    }
};
