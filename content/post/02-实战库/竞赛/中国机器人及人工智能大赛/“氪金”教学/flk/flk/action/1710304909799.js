Blockly.Blocks['1710304909799'] = {
  init: function() {
    this.jsonInit({
      "type": "1710304909799",
      "message0": "抱块右走",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710304909799'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(40)\nMOTOmove19(42,38,173,58,113,70,121,83,155,178,35,115,85,130,77,123,128,71,100)\nMOTOwait()\nMOTOsetspeed(90)\nMOTOmove19(42,38,173,93,113,70,123,94,155,178,35,102,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710304909799'] = function(block) {
  let code = "robot.leju_action('抱块右走')\n";
  return code;
}

