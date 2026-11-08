Blockly.Blocks['1710306251194'] = {
  init: function() {
    this.jsonInit({
      "type": "1710306251194",
      "message0": "抱块右走pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710306251194'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(48)\nMOTOmove19(42,38,173,40,92,41,137,83,155,178,35,115,85,130,77,136,128,71,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(42,38,173,93,113,70,123,94,155,178,35,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(42,38,173,100,113,70,123,98,155,178,35,99,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710306251194'] = function(block) {
  let code = "robot.leju_action('抱块右走pro')\n";
  return code;
}

