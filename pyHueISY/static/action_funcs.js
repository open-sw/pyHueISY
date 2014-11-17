function filter_select(event, type_id) {
    document.getElementById(type_id).textContent = triggerTypes[event.target.value]["type_desc"];
}

function addTrigger()
{
    var elemNewRow = document.getElementById("trigger-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);
    elemInsertRow.removeAttribute("id");

    nTriggers += 1;

    var elem = elemInsertRow.getElementsByTagName("input")[0];

    elem.id = "remove-trigger-" + nTriggers;
    elem.className = "delete-button";
    elem.onclick = removeTrigger;

    elem = elemInsertRow.getElementsByTagName("select")[0];
    elem.id = "trigger-" + nTriggers;
    elem.name = "trigger[" + nTriggers + "]";
    elem.onchange = new Function("event", "filter_select(event, \"trigger-" + nTriggers + "-type\")");

    elem = elemInsertRow.getElementsByTagName("span")[0];
    elem.id = "trigger-" + nTriggers + "-type";

    var elemList = elemInsertRow.getElementsByClassName("prototype-elements");

    while (elemList.length > 0 ) {
        elemList[0].className = "";
    }

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);
}

function removeTrigger(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);
    }
}

function addScene()
{
    var elemNewRow = document.getElementById("scene-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);

    nScenes += 1;

    elemInsertRow.removeAttribute("id");

    var elemSelect = elemInsertRow.getElementsByTagName("select")[0];

    elemSelect.id = "scene-" + nScenes;
    elemSelect.name = "scene[" + nScenes + "]";

    var elemInputList = elemInsertRow.getElementsByTagName("input");

    elemInputList[0].id = "remove-scene-" + nScenes;
    elemInputList[0].className = "delete-button";
    elemInputList[0].onclick = removeScene;

    elemInputList[1].id = "move-scene-up-" + nScenes;
    elemInputList[2].id = "move-scene-down-" + nScenes;

    var elemList = elemInsertRow.getElementsByClassName("prototype-elements");

    while (elemList.length > 0 ) {
        elemList[0].className = "";
    }

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);

    update_move_scene_buttons(elemNewRow.parentNode);
}

function removeScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);

        update_move_scene_buttons(tableNode);
    }
}

function update_move_scene_buttons(tableNode) {
    var upButtons = tableNode.getElementsByClassName("move-up-button");
    var index;

    upButtons[0].disabled = true;

    for (index = 1; index < upButtons.length - 1; index++) {
        upButtons[index].disabled = false;
    }

    var downButtons = tableNode.getElementsByClassName("move-down-button");

    for (index = 0; index < upButtons.length - 2; index++) {
        downButtons[index].disabled = false;
    }

    if (downButtons.length > 1) {
        downButtons[downButtons.length - 2].disabled = true;
    }
}

function moveUpScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByTagName("select")[0];

        var prevRowNode;
        for (prevRowNode = rowNode.previousElementSibling; prevRowNode != null; prevRowNode = prevRowNode.previousElementSibling) {
            if (prevRowNode.tagName != null && prevRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (prevRowNode != null) {
            var elemPrevious = prevRowNode.getElementsByTagName("select")[0];

            var indexCurrent = elemCurrent.selectedIndex;
            elemCurrent.selectedIndex = elemPrevious.selectedIndex;
            elemPrevious.selectedIndex = indexCurrent;
        }
    }
}

function moveDownScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByTagName("select")[0];

        var nextRowNode = null;
        for (nextRowNode = rowNode.nextElementSibling; nextRowNode != null; nextRowNode = nextRowNode.nextElementSibling) {
            if (nextRowNode.tagName != null && nextRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (nextRowNode != null) {
            var elemNext = nextRowNode.getElementsByTagName("select")[0];

            var indexCurrent = elemCurrent.selectedIndex;
            elemCurrent.selectedIndex = elemNext.selectedIndex;
            elemNext.selectedIndex = indexCurrent;
        }
    }
}

function getContainingRow(node) {
    var rowNode = null;
    for (rowNode = node.parentNode; rowNode != null; rowNode = rowNode.parentNode) {
        if (rowNode.tagName.toUpperCase() == "TR") {
            break;
        }
    }
    return rowNode;
}
