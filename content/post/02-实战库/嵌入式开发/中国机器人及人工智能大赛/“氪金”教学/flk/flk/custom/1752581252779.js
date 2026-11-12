Blockly.Blocks['1752581252779'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581252779",
      "message0": "大前进",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581252779'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(58,24,190,100,93,55,124,100,123,188,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(58,24,190,90,91,47,133,86,123,188,10,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,190,86,125,95,110,90,123,188,10,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,86,113,37,156,88,123,188,10,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(58,24,190,107,100,56,124,111,123,188,10,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(58,24,190,106,95,54,123,113,123,188,10,114,75,105,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(58,24,190,106,93,54,123,111,123,188,10,114,87,163,44,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(58,24,190,88,71,45,107,90,123,188,10,93,100,144,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(58,24,190,86,125,95,110,90,123,188,10,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(8)\nMOTOmove19(58,24,190,100,93,55,124,100,123,188,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581252779'] = function(block) {
  let code = "robot.leju_action('大前进')\n";
  return code;
}

