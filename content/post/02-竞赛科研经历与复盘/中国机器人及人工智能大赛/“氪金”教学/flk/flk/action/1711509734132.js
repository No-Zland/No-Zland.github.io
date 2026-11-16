Blockly.Blocks['1711509734132'] = {
  init: function() {
    this.jsonInit({
      "type": "1711509734132",
      "message0": "阻挡右移",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711509734132'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(108,102,36,96,113,70,123,94,120,75,171,95,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(108,102,36,53,102,40,148,81,120,75,171,115,85,130,77,136,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(108,102,36,93,113,70,123,94,120,75,171,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(108,102,36,100,113,70,123,98,120,75,171,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711509734132'] = function(block) {
  let code = "robot.leju_action('阻挡右移')\n";
  return code;
}

