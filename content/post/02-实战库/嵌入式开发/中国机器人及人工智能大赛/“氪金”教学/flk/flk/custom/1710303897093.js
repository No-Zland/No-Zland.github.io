Blockly.Blocks['1710303897093'] = {
  init: function() {
    this.jsonInit({
      "type": "1710303897093",
      "message0": "抱块左走",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710303897093'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,75,109,78,117,69,155,178,35,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(42,38,173,93,113,70,123,94,155,178,35,102,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710303897093'] = function(block) {
  let code = "robot.leju_action('抱块左走')\n";
  return code;
}

