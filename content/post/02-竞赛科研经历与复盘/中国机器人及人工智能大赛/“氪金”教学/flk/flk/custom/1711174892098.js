Blockly.Blocks['1711174892098'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174892098",
      "message0": "db_Lturn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174892098'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,30,20,20,65,75,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,94,29,56,57,92,130,176,10,103,48,146,14,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nDelayMs(800)\n";
  return code;
}

Blockly.Python['1711174892098'] = function(block) {
  let code = "robot.leju_action('db_Lturn')\n";
  return code;
}

