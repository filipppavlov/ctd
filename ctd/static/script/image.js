function ImageControl(url, $canvas) {
    var img = null;
    var channel = 0;
    var images = [];
    var image = null;
    var onLoad = null;
    var ctx = $canvas[0].getContext('2d');
    var comparison = null;
    var srcRect = [0, 0, 0, 0];
    var zoom = 1;
    var linkedImage = null;

    function createCompatibleCanvas(image) {
        var canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        return canvas;
    }

    function getChannelData(image, transform) {
        var canvas = createCompatibleCanvas(image);
        var inCtx = canvas.getContext('2d');
        inCtx.drawImage(image, 0, 0);
        var inData = inCtx.getImageData(0, 0, image.width, image.height).data;
        var outData = inCtx.createImageData(image.width, image.height);
        var d = outData.data;
        for (var i = 0; i < inData.length; i += 4) {
            d[i + 0] = transform[0] * inData[i + 0] + transform[1] * inData[i + 1] + transform[2] * inData[i + 2] + transform[3] * inData[i + 3];
            d[i + 1] = transform[4] * inData[i + 0] + transform[5] * inData[i + 1] + transform[6] * inData[i + 2] + transform[7] * inData[i + 3];
            d[i + 2] = transform[8] * inData[i + 0] + transform[9] * inData[i + 1] + transform[10] * inData[i + 2] + transform[11] * inData[i + 3];
            d[i + 3] = 255;
        }
        inCtx.putImageData(outData, 0, 0);
        return canvas;
    }

    function paint() {
        ctx.clearRect(0, 0, $canvas[0].width, $canvas[0].height);

        updateWindowSize();
        var sx = srcRect[0] + (images[channel].width - srcRect[2]) / 2;
        var sy = srcRect[1] + (images[channel].height - srcRect[3]) / 2;
        var sw = srcRect[2];
        var sh = srcRect[3];
        var dx = 0;
        var dy = 0;
        var dw = $canvas[0].width;
        var dh = $canvas[0].height;
        if (sx < 0) {
            dx += -sx / (srcRect[2] - sx) * dw;
            sx = 0;
        }
        if (sy < 0) {
            dy += -sy / (srcRect[3] - sy) * dh;
            sy = 0;
        }
        if (sw > images[channel].width) {
            dw = images[channel].width / sw * dw;
            sw = images[channel].width;
        }
        if (sh > images[channel].height) {
            dh = images[channel].height / sh * dh;
            sh = images[channel].height;
        }
        ctx.drawImage(images[channel], sx, sy, sw, sh, dx, dy, dw, dh);
        if (comparison && comparison.channel(channel)) {
            ctx.drawImage(comparison.channel(channel), sx, sy, sw, sh, dx, dy, dw, dh);
        }
    }

    function updateWindowSize() {
        var oa = images[channel].width / images[channel].height;
        var ca = $canvas[0].width / $canvas[0].height;
        if (oa < ca) {
            srcRect[2] = zoom * images[channel].height * ca;
            srcRect[3] = zoom * images[channel].height;
        }
        else {
            srcRect[2] = zoom * images[channel].width;
            srcRect[3] = zoom * images[channel].width / ca;
        }
    }

    function constraintShift() {
        updateWindowSize();
        if (srcRect[2] > images[channel].width) {
            srcRect[0] = 0;
        }
        else {
            if (srcRect[0] < -(images[channel].width - srcRect[2]) / 2) {
                srcRect[0] = -(images[channel].width - srcRect[2]) / 2;
            }
            if (srcRect[0] > (images[channel].width - srcRect[2]) / 2) {
                srcRect[0] = (images[channel].width - srcRect[2]) / 2;
            }
        }
        if (srcRect[3] > images[channel].height) {
            srcRect[1] = 0;
        }
        else {
            if (srcRect[1] < -(images[channel].height - srcRect[3]) / 2) {
                srcRect[1] = -(images[channel].height - srcRect[3]) / 2;
            }
            if (srcRect[1] > (images[channel].height - srcRect[3]) / 2) {
                srcRect[1] = (images[channel].height - srcRect[3]) / 2;
            }
        }
    }

    function resize() {
        $canvas[0].width = $canvas.width();
        $canvas[0].height = $canvas.height();
    }

    this.resizeToFit = function () {
        if (image) {
            resize();
            paint();
        }
    };

    this.zoom = function (value) {
        zoom = value;
        constraintShift();
        paint();
    };
    this.offset = function (x, y) {
        srcRect[0] = x;
        srcRect[1] = y;
        constraintShift();
        paint();
    };
    this.link = function (other) {
        linkedImage = other;
    };

    var self = this;

    $canvas
    .mousedown(function(event) {
        event.preventDefault();
        var pageX = event.pageX;
        var pageY = event.pageY;
        $(window).mousemove(function(event) {
            event.preventDefault();
            srcRect[0] -= (event.pageX - pageX) / $canvas.width() * srcRect[2];
            srcRect[1] -= (event.pageY - pageY) / $canvas.height() * srcRect[3];
            constraintShift();
            pageX = event.pageX;
            pageY = event.pageY;
            paint();
            if (linkedImage) {
                linkedImage.offset(srcRect[0], srcRect[1]);
            }
        });
    })
    .mouseup(function(event) {
        event.preventDefault();
        $(window).unbind("mousemove");
    });

    $canvas.bind('mousewheel DOMMouseScroll', function(event) {
        event.preventDefault();
        var delta = event.originalEvent.wheelDelta || -event.originalEvent.detail * 120;
        if (image) {
            zoom += zoom * delta / 120 / 10;
            if (zoom > 1) {
                zoom = 1;
            }
            constraintShift();
            paint();
            if (linkedImage) {
                linkedImage.zoom(zoom);
            }
        }
        $(this).css({'top': $(this).position().top + (delta > 0 ? '+=40' : '-=40')});
    });

    $("<img/>")
        .attr("src", url)
        .load(function () {
            image = this;
            images.push(getChannelData(this, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]));
            images.push(null);
            images.push(null);
            images.push(null);
            images.push(null);
            srcRect = [0, 0, images[0].width, images[0].height];
            self.resizeToFit();
            resize();
            paint();
            if (onLoad) {
                onLoad.call(self);
            }
        });

    this.channel = function(ch) {
        if (typeof ch == 'undefined') {
            return channel;
        }
        if (ch > 4) {
            return this;
        }
        channel = ch;
        if (images.length) {
            if (!images[ch]) {
                switch (ch) {
                    case 1:
                        images[ch] = getChannelData(image, [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]);
                        break;
                    case 2:
                        images[ch] = getChannelData(image, [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]);
                        break;
                    case 3:
                        images[ch] = getChannelData(image, [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]);
                        break;
                    case 4:
                        images[ch] = getChannelData(image, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]);
                        break;
                }
            }
            paint();
        }
        return this;
    };
    this.load = function (cb) {
        onLoad = cb;
        if (image) {
            onLoad.call(image);
        }
        return this;
    };
    this.source = function () {
        return image;
    };
    this.comparison = function (c) {
        comparison = c;
        if (images.length) {
            paint();
        }
    };
}

function DimensionsDiffer() {
}

function ImageComparison(img1, img2, $histogram) {
    this.images = [];
    var result = null;
    var onComplete = null;
    var heatMap = null;
    var minThreshold = 0;
    var maxThreshold = 255;
    var workers = [];

    if (img1.source().width != img2.source().width || img1.source().height != img2.source().height) {
        throw new DimensionsDiffer()
    }

    function createHistogram(buckets) {
        var canvas = $histogram[0];
        canvas.width = 256;
        canvas.height = 64;
        var ctx = canvas.getContext('2d');
        var max = 0;
        for (var i = 0; i < 256; ++i) {
            max = Math.max(max, buckets[i]);
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        for (i = 0; i < 256; ++i) {
            if (buckets[i]) {
                ctx.moveTo(i, 64);
                ctx.lineTo(i, (max - buckets[i]) / max * 64);
            }
        }
        ctx.stroke();
    }

    function killWorkers() {
        for (var i = 0; i < workers.length; ++i) {
            workers[i].terminate();
        }
        workers = [];
    }

    function recalculate(rebuildHistogram) {
        killWorkers();
        var canvas1 = createCompatibleCanvas(img1.source());
        var context1 = canvas1.getContext('2d');
        context1.drawImage(img1.source(), 0, 0);

        var canvas2 = createCompatibleCanvas(img2.source());
        var context2 = canvas2.getContext('2d');
        context2.drawImage(img2.source(), 0, 0);

        var blockCount = 4;
        var blockSize = img1.source().height / blockCount;
        var start = 0;
        result = createCompatibleCanvas(img1.source());
        var finished = 0;
        var buckets = new Uint32Array(256);

        function onWorkerFinished(msg) {
            result.getContext('2d').putImageData(msg.data.data, 0, msg.data.index);
            for (var i = 0; i < 256; ++i) {
                buckets[i] += msg.data.buckets[i];
            }
            if (++finished >= blockCount && onComplete) {
                workers = [];
                if ($histogram && rebuildHistogram) {
                    createHistogram(buckets);
                }
                onComplete.call(this);
            }
        }
        for (var i = 0; i < blockCount; ++i) {
            if (i == blockCount - 1) {
                blockSize = img1.source().height - start;
            }
            var data1 = context1.getImageData(0, start, canvas1.width, blockSize);
            var data2 = context2.getImageData(0, start, canvas2.width, blockSize);
            var worker = new Worker('/static/script/compareworker.js');
            worker.onmessage = onWorkerFinished;
            workers.push(worker);
            var msg = {'data0': data1, 'data1': data2, 'heatMap': heatMap, 'index': start, 'min': minThreshold, 'max': maxThreshold};
            worker.postMessage(msg);
        }
    }

    $("<img/>").attr("src", "/static/images/heatmap.png").load(function() {
        heatMap = getImagePixels(this);
        recalculate(true);
    });

    this.complete = function (cb) {
        onComplete = cb;
        if (result) {
            onComplete.call(this);
        }
        return this;
    };

    function createCompatibleCanvas(image) {
        var canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        return canvas;
    }
    function getImagePixels(image) {
        var canvas = createCompatibleCanvas(image);
        var context = canvas.getContext('2d');
        context.drawImage(image, 0, 0);
        return context.getImageData(0, 0, canvas.width, canvas.height).data;
    }

    this.channel = function () {
        return result;
    };

    this.thresholds = function (min, max) {
        var recalc = false;
        if (min != minThreshold) {
            minThreshold = min;
            recalc = true;
        }
        if (max != maxThreshold) {
            maxThreshold = max;
            recalc = true;
        }
        if (heatMap && recalc) {
            recalculate(false);
        }
    };
}