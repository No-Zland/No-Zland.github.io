Blockly.Blocks['1711509041852'] = {
  init: function() {
    this.jsonInit({
      "type": "1711509041852",
      "message0": "游泳右移",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711509041852'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(66,21,190,53,102,40,148,81,129,174,10,115,85,130,77,136,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(66,21,190,93,113,70,123,94,129,174,10,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711509041852'] = function(block) {
  let code = "robot.leju_action('游泳右移')\n";
  return code;
}

