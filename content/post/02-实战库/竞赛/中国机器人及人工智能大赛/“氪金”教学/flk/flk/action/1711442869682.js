Blockly.Blocks['1711442869682'] = {
  init: function() {
    this.jsonInit({
      "type": "1711442869682",
      "message0": "box_Lmove_dg1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711442869682'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,11,162,75,109,78,117,69,138,188,37,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(70)\nMOTOmove19(64,11,162,93,113,70,123,94,138,188,37,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(64,11,162,100,113,70,123,94,138,188,37,98,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711442869682'] = function(block) {
  let code = "robot.leju_action('box_Lmove_dg1')\n";
  return code;
}

