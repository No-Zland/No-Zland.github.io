Blockly.Blocks['1711517453106'] = {
  init: function() {
    this.jsonInit({
      "type": "1711517453106",
      "message0": "游泳右转dg1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711517453106'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(81,109,17,91,96,86,155,98,122,84,176,156,100,105,104,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711517453106'] = function(block) {
  let code = "robot.leju_action('游泳右转dg1')\n";
  return code;
}

