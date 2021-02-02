function makeDraggable(evt) {
    var svg = evt.target;
    var selectedElement = false;
    var lastSelectedElement = false;
    var selectedElementTransform;
    var offset;

    svg.addEventListener('mousedown', startDrag);
    svg.addEventListener('mousemove', drag);
    svg.addEventListener('mouseup', endDrag);
    svg.addEventListener('mouseleave', endDrag);
    svg.addEventListener('touchstart', startDrag);
    svg.addEventListener('touchmove', drag);
    svg.addEventListener('touchend', endDrag);
    svg.addEventListener('touchleave', endDrag);
    svg.addEventListener('touchcancel', endDrag);
    svg.addEventListener('focus', function () { this.addEventListener('keyup', deleteKeypoint) }, svg);

    function startDrag(evt) {
        if (evt.target.classList.contains('draggable')) {
            evt.target.classList.add('glow');
            selectedElement = evt.target.parentNode;
            offset = getMousePosition(evt);
            // Get all the transforms currently on this element
            var transforms = selectedElement.transform.baseVal;
            // Ensure the first transform is a translate transform
            if (transforms.length === 0 ||
                transforms.getItem(0).type !== SVGTransform.SVG_TRANSFORM_TRANSLATE) {
                // Create a transform that translates by (0, 0)
                var translate = svg.createSVGTransform();
                translate.setTranslate(0, 0);
                // Add the translation to the front of the transforms list
                selectedElement.transform.baseVal.insertItemBefore(translate, 0);
            }
            // Get initial translation amount
            selectedElementTransform = transforms.getItem(0);
            offset.x -= selectedElementTransform.matrix.e;
            offset.y -= selectedElementTransform.matrix.f;
        }
    }

    function drag(evt) {
        if (selectedElement) {
            evt.preventDefault();
            var coord = getMousePosition(evt);
            selectedElementTransform.setTranslate(coord.x - offset.x, coord.y - offset.y);
        }
    }

    function endDrag(evt) {
        if (selectedElement) {
            // send changed keypoints to flask
            sendData(selectedElement.getAttribute('keypoint_id'),
                selectedElementTransform.matrix.e,
                selectedElementTransform.matrix.f,
                1);

            updateData(selectedElement, selectedElementTransform.matrix.e, selectedElementTransform.matrix.f, 1)
        }
        //stop glowing if on
        evt.target.classList.remove('glow');

        // reset selectedElement
        lastSelectedElement = evt.target.parentNode;
        selectedElement = null;
    }

    function getMousePosition(evt) {
        var CTM = svg.getScreenCTM();
        if (evt.touches) { evt = evt.touches[0]; }
        return {
            x: (evt.clientX - CTM.e) / CTM.a,
            y: (evt.clientY - CTM.f) / CTM.d
        };
    }
    function deleteKeypoint(evt) {
        //if del or backspace is pressed, set the selected element to 0, 0 with confidence 0.
        if ((evt.keyCode === 46) || (evt.keyCode == 8)) {
            if (lastSelectedElement) {
                sendData(lastSelectedElement.getAttribute('keypoint_id'),
                    0, 0, 0.0);
                updateData(lastSelectedElement, 0, 0, 0);
                lastSelectedElement = null;
            }
        }
    }
}


// send changed keypoints to flask
function sendData(keypoint_id, x, y, conf) {
    var xhr = new XMLHttpRequest();
    var data = new FormData();
    data.append('keypoint_id', keypoint_id);
    data.append('x', x);
    data.append('y', y);
    data.append('conf', conf);
    xhr.open('POST', '/update_data')
    xhr.send(data)
}
// update changed keypoints in svg elements
function updateData(selectedElement, x, y, conf) {
    selectedElement.setAttribute('conf', conf);
    selectedElement.transform.baseVal[0].setTranslate(x, y);
    var textElement = selectedElement.getElementsByTagName('text').tooltipText;
    textElement.innerHTML = textElement.innerHTML.slice(0, textElement.innerHTML.indexOf(":") + 2) + Math.floor(conf * 100) + "%";
}

// view options 
function showSkeleton(cb) {
    if (cb.checked) {
        document.querySelectorAll('g[keypoint_id*="_0_"] circle').forEach(item => item.classList.remove('hidden'))
    }
    else {
        document.querySelectorAll('g[keypoint_id*="_0_"] circle').forEach(item => item.classList.add('hidden'))
    }
}
function showFace(cb) {
    if (cb.checked) {
        document.querySelectorAll('g[keypoint_id*="_1_"] circle').forEach(item => item.classList.remove('hidden'))
    }
    else {
        document.querySelectorAll('g[keypoint_id*="_1_"] circle').forEach(item => item.classList.add('hidden'))
    }
}
function showHands(cb) {
    if (cb.checked) {
        document.querySelectorAll('g[keypoint_id*="_2_"] circle').forEach(item => item.classList.remove('hidden'))
        document.querySelectorAll('g[keypoint_id*="_3_"] circle').forEach(item => item.classList.remove('hidden'))
    }
    else {
        document.querySelectorAll('g[keypoint_id*="_2_"] circle').forEach(item => item.classList.add('hidden'))
        document.querySelectorAll('g[keypoint_id*="_3_"] circle').forEach(item => item.classList.add('hidden'))
    }
}

// search keypoint
function searchKeypoint() {
    var searchKeyword = document.getElementById("searchKeyword").value;
    var svg_ele = document.getElementsByTagName("svg")[0];
    var w = svg_ele.viewBox.baseVal.width;
    var h = svg_ele.viewBox.baseVal.height;

    var g_keypoint = document.querySelector('g[keypoint_id="' + searchKeyword + '"]');
    g_keypoint.transform.baseVal[0].setTranslate(w / 2, h / 2);

    var cir_keypoint = document.querySelector('g[keypoint_id="' + searchKeyword + '"] circle');
    cir_keypoint.classList.add('glow');

    return true;
}

// save keypoints to json
function saveKeypoints() {
    var xhr = new XMLHttpRequest();
    var data = new FormData();
    data.append('save', 1);
    xhr.open('POST', '/save_json')
    xhr.send(data)
}

//submit form when 'Enter' key is pressed while in submitSearch
document.getElementById("searchKeyword").addEventListener("keyup", function (event) {
    if (event.keyCode === 13) {
        searchKeypoint();
    }
});