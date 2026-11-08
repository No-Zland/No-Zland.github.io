Blockly.Blocks['1711262925857'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262925857",
      "message0": "dbbox_down",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262925857'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,52,152,150,56,60,130,176,10,140,40,50,139,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67,27,161,52,152,150,56,60,128,178,40,140,40,50,139,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(130)\nMOTOmove19(66,74,161,52,152,150,56,60,128,130,39,140,40,50,139,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711262925857'] = function(block) {
  let code = "robot.leju_action('dbbox_down')\n";
  return code;
}

