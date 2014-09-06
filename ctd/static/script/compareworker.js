onmessage = function (msg) {
    var pixels1 = msg.data.data0.data;
    var pixels2 = msg.data.data1.data;
    var heatMap = msg.data.heatMap;
    var buckets = new Uint32Array(256);
    var range = 255 / (msg.data.max - msg.data.min);
    var threshold = msg.data.min;
    for (var i = 0; i < pixels1.length; i += 4) {
        var error = 0;
        for (var j = i; j < i + 4; ++j) {
            error = Math.max(error, Math.abs(pixels1[j] - pixels2[j]));
        }
        ++buckets[error];
        if (error < threshold) {
            for (j = 0; j < 4; ++j) {
                pixels1[i + j] = 0;
            }
        }
        else {
            error = Math.min(255, Math.floor((error - threshold) * range));
            for (j = 0; j < 4; ++j) {
                pixels1[i + j] = heatMap[error * 4 + j];
            }
        }
    }
    postMessage({'data': msg.data.data0, 'index': msg.data.index, 'buckets': buckets});
}