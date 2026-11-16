Blockly.Blocks['1711174769260'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174769260",
      "message0": "db_Rturn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174769260'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,91,132,34,190,91,130,176,10,106,167,138,137,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711174769260'] = function(block) {
  let code = "robot.leju_action('db_Rturn')\n";
  return code;
}

