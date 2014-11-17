function addColor()
{
    var elemNewRow = document.getElementById("color-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);

    nColors += 1;

    elemInsertRow.removeAttribute("id")

    var inputList = elemInsertRow.getElementsByTagName("input");

    inputList[0].id = "remove-color-" + nColors;
    inputList[0].className = "delete-button";
    inputList[0].onclick = removeColor;

    inputList[1].id = "move-color-up-" + nColors;
    inputList[2].id = "move-color-down-" + nColors;

    inputList[3].id = "color-" + nColors;
    inputList[3].name = "color[" + nColors + "]";
    inputList[3].color = new jscolor.color(inputList[3], {});

    var elemList = elemInsertRow.getElementsByClassName("prototype-elements");

    while (elemList.length > 0 ) {
        elemList[0].className = "";
    }

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);

    update_move_color_buttons(elemNewRow.parentNode);
}

function removeColor(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);

        update_move_color_buttons(tableNode);
    }
}

function update_move_color_buttons(tableNode) {
    var index;
    var upButtons = tableNode.getElementsByClassName("move-up-button");

    if (upButtons.length > 1) {
        upButtons[0].disabled = true;

        for (index = 1; index < upButtons.length - 1; index++) {
            upButtons[index].disabled = false;
        }
    }

    var downButtons = tableNode.getElementsByClassName("move-down-button");

    if (downButtons.length > 1) {
        for (index = 0; index < downButtons.length - 2; index++) {
            downButtons[index].disabled = false;
        }

        downButtons[downButtons.length - 2].disabled = true;
    }
}

function moveUpColor(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByClassName("color")[0];

        var prevRowNode;
        for (prevRowNode = rowNode.previousSibling; prevRowNode != null; prevRowNode = prevRowNode.previousSibling) {
            if (prevRowNode.tagName != null && prevRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (prevRowNode != null) {
            var elemPrevious = prevRowNode.getElementsByClassName("color")[0];

            var valCurrent = elemCurrent.value;
            elemCurrent.value = elemPrevious.value;
            elemPrevious.value = valCurrent;

            elemCurrent.color.importColor();
            elemPrevious.color.importColor();
        }
    }
}

function moveDownColor(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByClassName("color")[0];

        var nextRowNode;
        for (nextRowNode = rowNode.nextSibling; nextRowNode != null; nextRowNode = nextRowNode.nextSibling) {
            if (nextRowNode.tagName != null && nextRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (nextRowNode != null) {
            var elemNext = nextRowNode.getElementsByClassName("color")[0];

            var valCurrent = elemCurrent.value;
            elemCurrent.value = elemNext.value;
            elemNext.value = valCurrent;

            elemCurrent.color.importColor();
            elemNext.color.importColor();
        }
    }
}

function addLight()
{
    var elemNewRow = document.getElementById("light-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);
    elemInsertRow.removeAttribute("id");

    nLights += 1;

    var elem = elemInsertRow.getElementsByTagName("select")[0];
    elem.name = "light[" + nLights + "][light]";

    var elemListInput = elemInsertRow.getElementsByTagName("input");

    for (var index = 0; index < elemListInput.length; index++) {
        elem = elemListInput[index];
        switch (elem.id) {
            case "auto-new":
                elem.id = "auto-" + nLights;
                elem.name = "light[" + nLights + "][mode]";
                elem.onclick = new Function("document.getElementById(\"light-" + nLights + "-color\").disabled = true;");
                break;

            case "manual-new":
                elem.id = "manual-" + nLights;
                elem.name = "light[" + nLights + "][mode]";
                elem.onclick = new Function("document.getElementById(\"light-" + nLights + "-color\").disabled = false;");
                break;

            case "off-new":
                elem.id = "off-" + nLights;
                elem.name = "light[" + nLights + "][mode]";
                elem.onclick = new Function("document.getElementById(\"light-" + nLights + "-color\").disabled = true;");
                break;

            case "light-new-color":
                elem.id = "light-" + nLights + "-color";
                elem.name = "light[" + nLights + "][color]";
                elem.color = new jscolor.color(elem, {});
                break;

            case "add-light":
                elem.id = "remove-light-" + nLights;
                elem.className = "delete-button";
                elem.onclick = removeLight;
                break;
        }
    }

    var elemListLabel = elemInsertRow.getElementsByTagName("label");

    for (var index = 0; index < elemListLabel.length; index++) {
        elem = elemListLabel[index];
        switch (elem.id) {
            case "auto-new-label":
                elem.id = "auto-label-" + nLights;
                elem.setAttribute("for", "auto-" + nLights);
                break;

            case "manual-new-label":
                elem.id = "manual-label-" + nLights;
                elem.setAttribute("for", "manual-" + nLights);
                break;

            case "off-new-label":
                elem.id = "off-label-" + nLights;
                elem.setAttribute("for", "off-" + nLights);
                break;
        }
    }

    var elemList = elemInsertRow.getElementsByClassName("prototype-elements");

    while (elemList.length > 0 ) {
        elemList[0].className = "";
    }

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);
}

function removeLight(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);
    }
}
function getContainingRow(node) {
    var rowNode = null;
    for (var rowNode = node.parentNode; rowNode != null; rowNode = rowNode.parentNode) {
        if (rowNode.tagName.toUpperCase() == "TR") {
            break;
        }
    }
    return rowNode;
}
