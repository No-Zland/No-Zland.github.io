Blockly.Blocks['1752581376733'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581376733",
      "message0": "大左转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581376733'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(25)\nMOTOmove19(58,24,189,95,49,50,87,96,123,188,10,97,88,181,20,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,189,100,93,55,124,100,123,188,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581376733'] = function(block) {
  let code = "robot.leju_action('大左转')\n";
  return code;
}

