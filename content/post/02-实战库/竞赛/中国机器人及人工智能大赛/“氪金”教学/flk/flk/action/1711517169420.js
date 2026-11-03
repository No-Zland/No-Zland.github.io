Blockly.Blocks['1711517169420'] = {
  init: function() {
    this.jsonInit({
      "type": "1711517169420",
      "message0": "游泳左转dg",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711517169420'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(81,109,17,53,106,78,73,98,122,84,176,119,105,133,42,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711517169420'] = function(block) {
  let code = "robot.leju_action('游泳左转dg')\n";
  return code;
}

