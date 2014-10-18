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

    inputList[1].id = "color-" + nColors;
    inputList[1].name = "color[" + nColors + "]";
    inputList[1].color = new jscolor.color(inputList[1], {});

    var tdList = elemInsertRow.getElementsByTagName("td");

    var elemMoveUp = document.createElement('input');
    elemMoveUp.id = "move-color-up-" + nColors;
    elemMoveUp.className = "move-up-button";
    elemMoveUp.setAttribute("type", "button");
    elemMoveUp.onclick = moveUpColor;

    var elemMoveUpDiv = document.createElement("div");
    elemMoveUpDiv.appendChild(elemMoveUp);
    var elemMoveUpTD = document.createElement("td");

    tdList[1].appendChild(elemMoveUpDiv);

    var elemMoveDown = document.createElement('input');
    elemMoveDown.id = "move-color-down-" + nColors;
    elemMoveDown.className = "move-down-button";
    elemMoveDown.setAttribute("type", "button");
    elemMoveDown.onclick = moveDownColor;

    var elemMoveDownDiv = document.createElement("div");
    elemMoveDownDiv.appendChild(elemMoveDown);

    tdList[2].appendChild(elemMoveDownDiv);

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
    var upButtons = tableNode.getElementsByClassName("move-up-button");

    for (index = 0; index < upButtons.length; index++) {
        upButtons[index].disabled = false;
    }
    upButtons[0].disabled = true;

    var downButtons = tableNode.getElementsByClassName("move-down-button");

    for (index = 0; index < upButtons.length; index++) {
        downButtons[index].disabled = false;
    }
    downButtons[downButtons.length - 1].disabled = true;
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

    var elemOrigSelect = elemNewRow.getElementsByTagName("select")[0];

    var elem = elemInsertRow.getElementsByTagName("select")[0];
    elem.name = "light[" + nLights + "][light]";
    elem.selectedIndex = elemOrigSelect.selectedIndex;

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
