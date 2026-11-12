Blockly.Blocks['1711515428378'] = {
  init: function() {
    this.jsonInit({
      "type": "1711515428378",
      "message0": "阻挡左侧移",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711515428378'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,75,109,78,117,69,122,84,176,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(81,109,17,93,113,70,123,94,122,84,176,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,96,113,70,123,94,122,84,176,95,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,94,122,84,176,98,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711515428378'] = function(block) {
  let code = "robot.leju_action('阻挡左侧移')\n";
  return code;
}

