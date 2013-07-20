/* inspired by http://www.bitstorm.it/blog/en/2011/05/3d-sphere-html5-canvas/ */
var sphere = new Sphere3D();
var rotation = 0;
var distance = 0;
var x_rotate = 0;
var y_rotate = 0;
var z_rotate = 0;
var debug_enabled = false;
var manual_control = false;
var autorotate_timeout = 30;

// patch
var valueVertexMap ={0:231,3:232,6:233,9:234,12:235,15:236,18:237,21:238,24:239,27:240,30:241,33:242,36:243,39:244,42:206,45:205,48:204,51:203,54:202,57:201,60:200,63:199,66:198,69:197,72:196,75:195,78:194,81:193,84:154,87:155,90:156,93:157,96:158,99:159,102:160,105:161,108:162,111:163,114:164,117:165,120:166,123:167,126:168,129:169,132:131,135:130,138:129,141:128,144:127,147:126,150:125,153:124,156:123,159:122,162:121,165:120,168:119,171:118,174:117,177:116,180:78,183:79,186:80,189:81,192:82,195:83,198:84,201:85,204:86,207:87,210:88,213:89,216:90,219:91,222:92,225:93,228:55,231:54,234:53,237:52,240:51,243:50,246:49,249:48,252:47,255:46,258:45,261:44,264:43,267:42,270:41,273:40,276:2,279:3,282:4,285:5,288:6,291:7,294:8,297:9,300:10,303:11,306:12,309:13,312:14,315:15,318:16,321:17,324:359,327:358,330:357,333:356,336:355,339:354,342:353,345:352,348:351,351:350,354:349,357:348,360:347,363:346,366:345,369:344,372:383,375:384,378:385,381:386,384:387,387:388,390:389,393:390,396:391,399:392,402:393,405:394,408:395,411:396,414:433,417:432,420:431,423:430,426:429,429:428,432:427,435:426,438:425,441:424,444:423,447:422,450:461,453:462,456:463,459:464,462:465,465:466,468:467,471:468,474:469,477:470,480:507,483:506,486:505,489:504,492:503,495:502,498:501,501:500};

function Point3D() {
    this.x = 0;
    this.y = 0;
    this.z = 0;
    this.color = "";
}

function Sphere3D(radius) {
    this.point = new Array();
    this.radius = (typeof (radius) == "undefined") ? 25.0 : radius;
    this.radius = (typeof (radius) != "number") ? 25.0 : radius;
    this.numberOfVertexes = 0;

    for (alpha = 0; alpha <= 6.11; alpha += 0.165) {
        p = this.point[this.numberOfVertexes] = new Point3D();

        p.x = Math.cos(alpha) * this.radius;
        p.y = 0;
        p.z = Math.sin(alpha) * this.radius;

        this.numberOfVertexes++;
    }

    for (var direction = 1; direction >= -1; direction -= 2) {
        for (var beta = 0.17; beta < 1.445; beta += 0.165) {
            var radius = Math.cos(beta) * this.radius;
            var fixedY = Math.sin(beta) * this.radius * direction;
            for (var alpha = 0; alpha < 6.11; alpha += 0.165) {
                p = this.point[this.numberOfVertexes] = new Point3D();
                p.x = Math.cos(alpha) * radius;
                p.y = fixedY;
                p.z = Math.sin(alpha) * radius;

                this.numberOfVertexes++;
            }
        }
    }

}

function rotateY(point, radians) {
    var y = point.y;
    point.y = (y * Math.cos(radians)) + (point.z * Math.sin(radians) * -1.0);
    point.z = (y * Math.sin(radians)) + (point.z * Math.cos(radians));
}

function rotateX(point, radians) {
    var x = point.x;
    point.x = (x * Math.cos(radians)) + (point.z * Math.sin(radians) * -1.0);
    point.z = (x * Math.sin(radians)) + (point.z * Math.cos(radians));
}

function rotateZ(point, radians) {
    var x = point.x;
    point.x = (x * Math.cos(radians)) + (point.y * Math.sin(radians) * -1.0);
    point.y = (x * Math.sin(radians)) + (point.y * Math.cos(radians));
}

function projection(xy, z, xyOffset, zOffset, distance) {
    return ((distance * xy) / (z - zOffset)) + xyOffset;
}

function render() {
    var canvas = document.getElementById("sphere3d");
    var width = canvas.getAttribute("width");
    var height = canvas.getAttribute("height");
    var ctx = canvas.getContext('2d');
    var scale = distance/1000;
    var x, y;

    var p = new Point3D();

    ctx.save();
    ctx.clearRect(0, 0, width, height);

    ctx.globalCompositeOperation = "lighter";
    for (i = 0; i < sphere.numberOfVertexes; i++) {

        p.x = sphere.point[i].x;
        p.y = sphere.point[i].y;
        p.z = sphere.point[i].z;
        p.color = sphere.point[i].color;

        rotateY(p, rotation+y_rotate);
        rotateX(p, rotation+x_rotate);
        rotateZ(p, rotation+z_rotate);

        x = projection(p.x, p.z, width / 2.0, 100.0, distance);
        y = projection(p.y, p.z, height / 2.0, 100.0, distance);
        if ((x >= 0) && (x < width)) {
            if ((y >= 0) && (y < height)) {
                if (p.color == "") {
                    drawPoint(ctx, x, y, 4*scale, "rgba(100,100,100,0.2)");
                } else {
                    drawPoint(ctx, x, y, 15*scale, "rgba(100,100,100,0.2)");
                    drawPoint(ctx, x, y, 15*scale, p.color);
                }
            }
        }
    }
    ctx.restore();
    ctx.fillStyle = "rgb(150,150,150)";
    if (debug_enabled) {
      ctx.fillText('dist: ' + distance + ' rot: ' + rotation.toFixed(2) + ' xrot: ' + x_rotate.toFixed(2) + ' yrot: ' + y_rotate.toFixed(2) + " @jeffnappi", width - 250, height - 5);
    } else {
      ctx.fillText(" @jeffnappi", width - 90, height - 5);
    }
    if (!manual_control) {
      if (distance < 1000) {
        distance += 10;
        rotation += Math.PI / 90.0;
      } else if (rotation > 0) {
        rotation -= Math.PI / 90.0;
      }
    }
}

function drawPoint(ctx, x, y, size, color) {
    ctx.save();
    ctx.beginPath();
    ctx.fillStyle = color;
    ctx.arc(x, y, size, 0, 2 * Math.PI, true);
    ctx.fill();
    ctx.restore();
}

function drawPointWithGradient(ctx, x, y, size, color, gradient) {
    var reflection;

    reflection = size / 4;

    ctx.save();
    ctx.translate(x, y);
    var radgrad = ctx.createRadialGradient(-reflection, -reflection, reflection, 0, 0, size);

    radgrad.addColorStop(0, '#aaaaaa');
    radgrad.addColorStop(gradient, color);
    radgrad.addColorStop(1, 'rgba(0,0,0,1)');

    ctx.fillStyle = radgrad;
    ctx.fillRect(-size, -size, size * 2, size * 2);
    ctx.restore();
}

function valueMap(values) {
    for (x = 0; x < values.length; x += 3) {
        if (valueVertexMap[x] != undefined) {
            sphere.point[valueVertexMap[x]].color = "rgb(" + values[x] + ',' + values[x + 1] + ',' + values[x + 2] + ')';
        }
    }
}

function display_init() {
    $('#reset').click(function() {
        manual_control = false;
        distance = rotation = x_rotate = y_rotate = z_rotate = 0;
    });

    var $canvas = $('#sphere3d')

    $canvas.bind('mousewheel', function(e) {
        manual_control = true;
        var newDistance = distance + e.originalEvent.wheelDelta;
        if (newDistance > 0 && newDistance < 1500) {
            distance = newDistance;
        }
        e.preventDefault();
    });

    var mouseDown = false;
    var mouseYDragOffset;
    var mouseXDragOffset;

    $canvas.bind('mousedown', function(e) {
        manual_control = true;
        mouseYDragOffset = e.pageY;
        mouseXDragOffset = e.pageY;
        mouseDown = true;
    });

    $canvas.bind('mouseup', function(e) {
        mouseDown = false;
    });

    $canvas.bind('mouseleave', function(e) {
        mouseDown = false;
    });

    $canvas.bind('mousemove', function (e) {
        if (mouseDown) {
            x_rotate = 2*Math.PI * ((e.pageX - mouseXDragOffset)/300);
            y_rotate = Math.PI * ((e.pageY - mouseYDragOffset)/300);
        }
    });

    var values = [];
    var frame = 0;

    if ("WebSocket" in window) {
      var ws = new WebSocket(location.origin.replace('http','ws') + "/realtime/");
      ws.onopen = function() {};
      ws.onmessage = function (evt) {
          var values = JSON.parse(evt.data);
          valueMap(values);
      };
      ws.onclose = function() {};
    } else {
      alert("WebSocket not supported");
    }

    if (autorotate_timeout!=0 && autorotate_timeout != undefined) {
      setInterval(function() {
          if (!manual_control) {
              rotation = Math.PI;
          }
      }, 1000 * autorotate_timeout);
    }

  // Set framerate to 30 fps
    setInterval(function () {
        render();
    }, 1000/30 );
}
