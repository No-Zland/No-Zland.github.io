Blockly.Blocks['1710334402667'] = {
  init: function() {
    this.jsonInit({
      "type": "1710334402667",
      "message0": "抱箱前进1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710334402667'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(6)\nMOTOmove19(65, 10, 149, 90, 91, 48, 134, 88, 140, 190, 50, 94, 109, 146, 71, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 123, 95, 115, 90, 140, 190, 50, 94, 109, 146, 71, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 121, 37, 161, 88, 140, 190, 50, 94, 109, 146, 72, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 107, 98, 56, 129, 111, 140, 190, 50, 112, 131, 155, 88, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 106, 93, 54, 128, 113, 140, 190, 50, 114, 77, 105, 85, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 106, 91, 54, 128, 111, 140, 190, 50, 114, 89, 163, 39, 112, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 88, 69, 45, 112, 90, 140, 190, 50, 93, 102, 144, 71, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 123, 95, 115, 90, 140, 190, 50, 94, 107, 146, 72, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 100, 91, 55, 129, 100, 140, 190, 50, 100, 109, 145, 71, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710334402667'] = function(block) {
  let code = "robot.leju_action('抱箱前进1')\n";
  return code;
}

Blockly.Blocks['1710334409340'] = {
  init: function() {
    this.jsonInit({
      "type": "1710334409340",
      "message0": "抱箱后退1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710334409340'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(5)\nMOTOmove19(65, 10, 149, 90, 91, 48, 138, 88, 140, 190, 50, 94, 107, 146, 67, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 90, 95, 94, 90, 140, 190, 50, 94, 107, 146, 67, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 88, 71, 53, 114, 85, 140, 190, 50, 93, 100, 144, 70, 91, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 106, 93, 53, 134, 111, 140, 190, 50, 114, 87, 163, 33, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 106, 95, 53, 133, 113, 140, 190, 50, 114, 110, 105, 105, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 107, 100, 56, 130, 109, 140, 190, 50, 112, 129, 147, 86, 115, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 107, 100, 56, 130, 109, 140, 190, 50, 112, 129, 147, 86, 115, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 86, 113, 37, 167, 90, 140, 190, 50, 94, 107, 147, 67, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 90, 95, 95, 90, 140, 190, 50, 94, 105, 147, 69, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 100, 93, 55, 133, 100, 140, 190, 50, 100, 107, 145, 67, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710334409340'] = function(block) {
  let code = "robot.leju_action('抱箱后退1')\n";
  return code;
}

Blockly.Blocks['1710335656590'] = {
  init: function() {
    this.jsonInit({
      "type": "1710335656590",
      "message0": "抱箱右转1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710335656590'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,65,65,65,65,30,30,30,65,65,65,65,65,0,0,0)\nMOTOsetspeed(14)\nMOTOmove19(65, 10, 149, 95, 110, 55, 149, 95, 140, 190, 50, 105, 130, 145, 91, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(65, 10, 149, 95, 118, 55, 149, 92, 140, 190, 50, 105, 121, 145, 91, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(14)\nMOTOmove19(65, 10, 149, 100, 90, 55, 129, 100, 140, 190, 50, 100, 110, 145, 71, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(400)\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 100, 90, 55, 129, 100, 140, 190, 50, 100, 110, 145, 71, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710335656590'] = function(block) {
  let code = "robot.leju_action('抱箱右转1')\n";
  return code;
}

Blockly.Blocks['1710335685798'] = {
  init: function() {
    this.jsonInit({
      "type": "1710335685798",
      "message0": "抱箱左转1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710335685798'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,65,65,65,65,30,30,30,65,65,65,65,65,0,0,0)\nMOTOsetspeed(14)\nMOTOmove19(65, 10, 149, 95, 71, 55, 109, 95, 140, 190, 50, 105, 89, 145, 51, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(65, 10, 149, 95, 80, 55, 109, 92, 140, 190, 50, 105, 81, 145, 51, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(14)\nMOTOmove19(65, 10, 149, 100, 91, 55, 129, 100, 140, 190, 50, 100, 109, 145, 71, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(400)\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 100, 91, 55, 129, 100, 140, 190, 50, 100, 109, 145, 71, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710335685798'] = function(block) {
  let code = "robot.leju_action('抱箱左转1')\n";
  return code;
}

Blockly.Blocks['1710422585740'] = {
  init: function() {
    this.jsonInit({
      "type": "1710422585740",
      "message0": "后退2(1)",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710422585740'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 99, 58, 51, 106, 100, 120, 170, 100, 102, 109, 134, 75, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 105, 91, 56, 132, 96, 120, 170, 100, 107, 126, 114, 108, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710422585740'] = function(block) {
  let code = "robot.leju_action('后退2(1)')\n";
  return code;
}

Blockly.Blocks['1710885775371'] = {
  init: function() {
    this.jsonInit({
      "type": "1710885775371",
      "message0": "fast2",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710885775371'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,10,55,65,90,80,50,25,25,10,55,65,90,80,50,0,0,0)\nMOTOsetspeed(45)\nMOTOmove19(80, 30, 100, 99, 93, 54, 122, 90, 120, 170, 100, 98, 107, 146, 75, 95, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 89, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 89, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 120, 99, 91, 66, 111, 102, 120, 170, 120, 101, 85, 101, 97, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 86, 63, 111, 100, 120, 170, 120, 101, 90, 126, 79, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 89, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 89, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 120, 99, 91, 66, 111, 102, 120, 170, 120, 101, 85, 101, 97, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 86, 63, 111, 100, 120, 170, 120, 101, 90, 126, 79, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(65)\nMOTOmove19(80, 30, 80, 96, 95, 70, 110, 100, 120, 170, 80, 102, 109, 146, 75, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710885775371'] = function(block) {
  let code = "robot.leju_action('fast2')\n";
  return code;
}

Blockly.Blocks['1710885800975'] = {
  init: function() {
    this.jsonInit({
      "type": "1710885800975",
      "message0": "fastforward2s",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710885800975'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,10,55,65,90,80,50,25,25,10,55,65,90,80,50,0,0,0)\nMOTOsetspeed(45)\nMOTOmove19(80, 30, 100, 99, 93, 54, 122, 90, 120, 170, 100, 98, 107, 146, 75, 95, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 89, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 89, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 120, 99, 91, 66, 111, 102, 120, 170, 120, 101, 85, 101, 97, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 86, 63, 111, 100, 120, 170, 120, 101, 90, 126, 79, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 80, 99, 115, 99, 103, 100, 120, 170, 80, 101, 109, 134, 89, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 74, 121, 100, 120, 170, 80, 101, 114, 137, 89, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 80, 99, 110, 61, 126, 104, 120, 170, 80, 101, 100, 127, 94, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(80, 30, 120, 99, 91, 66, 111, 102, 120, 170, 120, 101, 85, 101, 97, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 86, 63, 111, 100, 120, 170, 120, 101, 90, 126, 79, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 120, 99, 100, 73, 106, 100, 120, 170, 120, 101, 90, 139, 74, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(65)\nMOTOmove19(80, 30, 80, 96, 95, 70, 110, 100, 120, 170, 80, 102, 109, 146, 75, 96, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710885800975'] = function(block) {
  let code = "robot.leju_action('fastforward2s')\n";
  return code;
}

Blockly.Blocks['1710886016521'] = {
  init: function() {
    this.jsonInit({
      "type": "1710886016521",
      "message0": "抱箱后退1（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710886016521'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(5)\nMOTOmove19(65, 10, 149, 90, 91, 48, 138, 88, 140, 190, 50, 94, 107, 146, 67, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 90, 95, 94, 90, 140, 190, 50, 94, 107, 146, 67, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 88, 71, 53, 114, 85, 140, 190, 50, 93, 100, 144, 70, 91, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 106, 93, 53, 134, 111, 140, 190, 50, 114, 87, 163, 33, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 106, 95, 53, 133, 113, 140, 190, 50, 114, 110, 105, 105, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 107, 100, 56, 130, 109, 140, 190, 50, 112, 129, 147, 86, 115, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 107, 100, 56, 130, 109, 140, 190, 50, 112, 129, 147, 86, 115, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(65, 10, 149, 86, 113, 37, 167, 90, 140, 190, 50, 94, 107, 147, 67, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 86, 90, 95, 95, 90, 140, 190, 50, 94, 105, 147, 69, 87, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 10, 149, 100, 93, 55, 133, 100, 140, 190, 50, 100, 107, 145, 67, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710886016521'] = function(block) {
  let code = "robot.leju_action('抱箱后退1（2）')\n";
  return code;
}

Blockly.Blocks['1710886315365'] = {
  init: function() {
    this.jsonInit({
      "type": "1710886315365",
      "message0": "抱k前进",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710886315365'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,10,55,65,90,80,50,25,25,10,55,65,90,80,50,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(70, 10, 183, 99, 93, 54, 122, 90, 136, 190, 22, 98, 107, 146, 75, 95, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(70, 10, 183, 99, 115, 99, 103, 100, 136, 190, 22, 98, 109, 134, 89, 98, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 110, 74, 121, 100, 136, 190, 22, 98, 114, 137, 89, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 110, 61, 126, 104, 136, 190, 22, 98, 100, 127, 94, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(70, 10, 183, 99, 91, 66, 111, 102, 136, 190, 22, 98, 85, 101, 97, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 86, 63, 111, 100, 136, 190, 22, 98, 90, 126, 79, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 100, 73, 106, 100, 136, 190, 22, 98, 90, 139, 74, 96, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(65)\nMOTOmove19(70, 10, 183, 96, 95, 70, 110, 100, 136, 190, 22, 98, 109, 146, 75, 96, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(70, 10, 183, 100, 93, 55, 124, 100, 136, 190, 22, 98, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710886315365'] = function(block) {
  let code = "robot.leju_action('抱k前进')\n";
  return code;
}

Blockly.Blocks['1710886322814'] = {
  init: function() {
    this.jsonInit({
      "type": "1710886322814",
      "message0": "抱k后退",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710886322814'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 100, 93, 55, 124, 100, 138, 186, 24, 100, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(60, 13, 177, 85, 91, 50, 128, 88, 138, 186, 24, 95, 117, 168, 62, 90, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(60, 13, 177, 88, 91, 48, 129, 88, 138, 186, 24, 94, 107, 146, 76, 87, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 86, 90, 95, 84, 90, 138, 186, 24, 94, 107, 146, 78, 87, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 88, 84, 53, 115, 85, 138, 186, 24, 93, 104, 144, 78, 91, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(60, 13, 177, 106, 93, 53, 124, 113, 138, 186, 24, 114, 102, 154, 55, 110, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 106, 93, 53, 124, 113, 138, 186, 24, 114, 95, 105, 95, 110, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(60, 13, 177, 104, 83, 32, 135, 111, 138, 186, 24, 115, 111, 150, 72, 112, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(60, 13, 177, 100, 93, 55, 124, 100, 138, 186, 24, 100, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710886322814'] = function(block) {
  let code = "robot.leju_action('抱k后退')\n";
  return code;
}

Blockly.Blocks['1711096067753'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096067753",
      "message0": "box-Rmove-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096067753'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(58, 20, 173, 100, 113, 70, 123, 98, 144, 184, 35, 99, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(58, 20, 173, 53, 102, 40, 148, 81, 144, 184, 35, 115, 85, 130, 77, 136, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58, 20, 173, 93, 113, 70, 123, 94, 144, 184, 35, 102, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58, 20, 173, 100, 113, 70, 123, 98, 144, 184, 35, 99, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096067753'] = function(block) {
  let code = "robot.leju_action('box-Rmove-q')\n";
  return code;
}

Blockly.Blocks['1711096097399'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096097399",
      "message0": "box-go-2min-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096097399'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 90, 91, 48, 129, 88, 137, 190, 23, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096097399'] = function(block) {
  let code = "robot.leju_action('box-go-2min-q')\n";
  return code;
}

Blockly.Blocks['1711096105829'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096105829",
      "message0": "box-go-4min-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096105829'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 90, 91, 48, 129, 88, 137, 190, 23, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096105829'] = function(block) {
  let code = "robot.leju_action('box-go-4min-q')\n";
  return code;
}

Blockly.Blocks['1711096125443'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096125443",
      "message0": "Rturn-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096125443'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 99, 160, 49, 190, 100, 120, 170, 85, 100, 161, 135, 148, 98, 120, 40, 100)\nMOTOwait()\nDelayMs(150)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096125443'] = function(block) {
  let code = "robot.leju_action('Rturn-q')\n";
  return code;
}

Blockly.Blocks['1711096138807'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096138807",
      "message0": "q-box-back",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096138807'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 108, 137, 190, 23, 111, 102, 136, 78, 112, 120, 40, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 107, 137, 190, 23, 107, 136, 154, 91, 103, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(71, 10, 180, 92, 116, 55, 144, 85, 137, 190, 23, 95, 107, 145, 76, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 92, 75, 55, 106, 95, 137, 190, 23, 95, 107, 145, 76, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 107, 137, 190, 23, 108, 84, 141, 56, 115, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(71, 10, 180, 105, 92, 55, 124, 107, 137, 190, 23, 111, 107, 136, 78, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 100, 93, 55, 124, 98, 137, 190, 23, 100, 107, 145, 76, 102, 120, 40, 100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1711096138807'] = function(block) {
  let code = "robot.leju_action('q-box-back')\n";
  return code;
}

Blockly.Blocks['1711096148448'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096148448",
      "message0": "q-L-turn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096148448'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 107, 89, 106, 59, 103, 120, 170, 100, 105, 51, 152, 21, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096148448'] = function(block) {
  let code = "robot.leju_action('q-L-turn')\n";
  return code;
}

Blockly.Blocks['1711096159612'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096159612",
      "message0": "q-box-Rmove",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096159612'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,65,55,55,55,35,20,20,20,65,85,95,85,35,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 90, 93, 50, 130, 95, 139, 190, 23, 134, 97, 124, 88, 116, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096159612'] = function(block) {
  let code = "robot.leju_action('q-box-Rmove')\n";
  return code;
}

Blockly.Blocks['1711096167186'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096167186",
      "message0": "q-box-Lmove",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096167186'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,14,20,65,85,95,85,35,20,20,20,65,55,55,55,35,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 72, 100, 68, 111, 84, 139, 190, 23, 119, 106, 154, 68, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(50)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096167186'] = function(block) {
  let code = "robot.leju_action('q-box-Lmove')\n";
  return code;
}

Blockly.Blocks['1711096178656'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096178656",
      "message0": "q-big-Rurn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096178656'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 99, 160, 49, 190, 100, 120, 170, 85, 100, 161, 135, 148, 98, 120, 40, 100)\nMOTOwait()\nDelayMs(150)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096178656'] = function(block) {
  let code = "robot.leju_action('q-big-Rurn')\n";
  return code;
}

Blockly.Blocks['1711096190074'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096190074",
      "message0": "q-box-6min",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096190074'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(80, 10, 174, 100, 93, 55, 124, 100, 120, 190, 24, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 10, 174, 90, 91, 48, 129, 88, 120, 190, 24, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 110, 95, 100, 90, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(80, 10, 174, 90, 91, 48, 129, 88, 120, 190, 24, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 10, 174, 100, 93, 55, 124, 100, 120, 190, 24, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096190074'] = function(block) {
  let code = "robot.leju_action('q-box-6min')\n";
  return code;
}

Blockly.Blocks['1711096200792'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096200792",
      "message0": "q-box-go3",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096200792'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(80, 10, 174, 100, 93, 55, 124, 100, 120, 190, 24, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 10, 174, 90, 91, 48, 129, 88, 120, 190, 24, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 125, 95, 110, 90, 120, 190, 24, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 113, 37, 156, 88, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80, 10, 174, 107, 100, 56, 124, 111, 120, 190, 24, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 95, 54, 123, 113, 120, 190, 24, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 106, 93, 54, 123, 111, 120, 190, 24, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 88, 71, 45, 107, 90, 120, 190, 24, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(80, 10, 174, 86, 110, 95, 100, 90, 120, 190, 24, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(80, 10, 174, 90, 91, 48, 129, 88, 120, 190, 24, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 10, 174, 100, 93, 55, 124, 100, 120, 190, 24, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096200792'] = function(block) {
  let code = "robot.leju_action('q-box-go3')\n";
  return code;
}

Blockly.Blocks['1711098187817'] = {
  init: function() {
    this.jsonInit({
      "type": "1711098187817",
      "message0": "q-box-up",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711098187817'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(64, 43, 93, 88, 148, 150, 69, 92, 120, 168, 115, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(77, 35, 150, 88, 148, 150, 69, 92, 119, 174, 51, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(79, 34, 146, 65, 130, 145, 46, 67, 121, 168, 55, 131, 64, 50, 155, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 141, 69, 124, 139, 47, 72, 137, 190, 55, 128, 67, 52, 152, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 180, 91, 114, 150, 48, 90, 137, 190, 23, 114, 84, 50, 151, 112, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 99, 107, 144, 75, 99, 120, 40, 99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711098187817'] = function(block) {
  let code = "robot.leju_action('q-box-up')\n";
  return code;
}

Blockly.Blocks['1711174602361'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174602361",
      "message0": "L-turn-00",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174602361'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,30,20,20,65,75,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 115, 94, 29, 56, 57, 92, 120, 170, 115, 103, 48, 146, 14, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(800)\n";
  return code;
}

Blockly.Python['1711174602361'] = function(block) {
  let code = "robot.leju_action('L-turn-00')\n";
  return code;
}

Blockly.Blocks['1711174609568'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174609568",
      "message0": "R-turn-00",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174609568'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(68, 32, 90, 91, 132, 34, 190, 91, 129, 162, 105, 106, 167, 138, 137, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711174609568'] = function(block) {
  let code = "robot.leju_action('R-turn-00')\n";
  return code;
}

Blockly.Blocks['1711175294884'] = {
  init: function() {
    this.jsonInit({
      "type": "1711175294884",
      "message0": "上台阶",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711175294884'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 1站立\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 2\nMOTOsetspeed(25)\nMOTOmove19(94, 79, 100, 85, 106, 79, 113, 80, 106, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(30)\nMOTOmove19(100, 150, 100, 100, 160, 78, 155, 100, 100, 100, 100, 100, 135, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 160, 78, 155, 100, 100, 100, 100, 100, 145, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(300)\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 2右腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 100, 100, 106, 93, 55, 124, 112, 103, 95, 100, 115, 68, 73, 115, 111, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 100, 100, 105, 115, 100, 101, 110, 100, 50, 100, 115, 40, 150, 20, 105, 128, 71, 100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 65, 50, 101, 100, 100, 50, 100, 100, 40, 122, 45, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 55, 50, 101, 100, 100, 100, 100, 100, 40, 122, 45, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(300)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 90, 70, 10, 160, 90, 100, 190, 20, 95, 40, 122, 65, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 45, 20, 95, 100, 100, 190, 20, 95, 85, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 130, 90, 105, 100, 100, 190, 20, 95, 95, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 85, 110, 90, 105, 100, 100, 100, 20, 95, 102, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 3左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(30)\nMOTOmove19(100, 150, 100, 100, 160, 78, 155, 100, 100, 100, 100, 100, 135, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 160, 78, 155, 100, 100, 100, 100, 100, 145, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(300)\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\n\n\n-- 15\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 180, 102, 79, 32, 137, 108, 100, 100, 20, 108, 121, 165, 70, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 100, 108, 70, 10, 148, 108, 100, 70, 100, 111, 101, 142, 72, 110, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,75,85,100,90,60,30,30,30,50,55,50,50,50,0,0,0)\n\n\n-- 4\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 105, 79, 32, 137, 108, 100, 70, 100, 107, 107, 160, 60, 112, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,50,60,60,60,60,30,30,30,50,60,60,60,60,0,0,0)\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 100, 79, 35, 130, 100, 100, 70, 100, 102, 107, 160, 65, 102, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 98, 79, 35, 130, 95, 100, 70, 100, 98, 107, 160, 65, 95, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 92, 79, 35, 130, 92, 100, 70, 100, 98, 121, 168, 63, 92, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 14\nMOTOsetspeed(20)\nMOTOmove19(80, 30, 100, 100, 95, 55, 123, 100, 120, 170, 100, 100, 105, 145, 77, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711175294884'] = function(block) {
  let code = "robot.leju_action('上台阶')\n";
  return code;
}

Blockly.Blocks['1711259016311'] = {
  init: function() {
    this.jsonInit({
      "type": "1711259016311",
      "message0": "001-前倒地",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711259016311'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\n\n\n-- 起\nMOTOsetspeed(100)\nMOTOmove19(80, 90, 101, 101, 93, 57, 124, 101, 131, 100, 98, 102, 107, 143, 77, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(37, 92, 182, 85, 64, 41, 98, 99, 153, 107, 19, 130, 142, 160, 92, 103, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(54, 47, 190, 63, 160, 136, 46, 86, 150, 147, 19, 137, 44, 67, 152, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(85, 12, 172, 62, 160, 146, 47, 75, 119, 189, 31, 139, 43, 54, 154, 123, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(54, 47, 190, 66, 149, 146, 55, 63, 150, 147, 19, 158, 48, 60, 146, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(54, 47, 190, 70, 126, 145, 53, 68, 150, 147, 19, 138, 74, 60, 147, 135, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(80, 30, 113, 100, 125, 140, 62, 100, 120, 170, 87, 100, 75, 60, 138, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(80, 30, 113, 102, 128, 104, 97, 100, 120, 170, 87, 102, 74, 91, 104, 100, 128, 71, 100)\nMOTOwait()\n\n\n-- 站立\nMOTOsetspeed(30)\nMOTOmove19(80, 37, 100, 108, 93, 55, 124, 100, 120, 170, 100, 92, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711259016311'] = function(block) {
  let code = "robot.leju_action('001-前倒地')\n";
  return code;
}

Blockly.Blocks['1711259057734'] = {
  init: function() {
    this.jsonInit({
      "type": "1711259057734",
      "message0": "001-后倒地",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711259057734'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,0,0,0)\nMOTOsetspeed(80)\nMOTOmove19(93, 100, 20, 101, 131, 126, 170, 100, 108, 100, 185, 99, 69, 74, 30, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(92, 16, 46, 100, 80, 150, 60, 100, 108, 184, 154, 100, 120, 50, 140, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(92, 18, 58, 100, 73, 150, 40, 100, 108, 182, 142, 100, 127, 50, 160, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(92, 25, 135, 100, 124, 150, 50, 100, 108, 175, 65, 100, 76, 50, 150, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711259057734'] = function(block) {
  let code = "robot.leju_action('001-后倒地')\n";
  return code;
}

Blockly.Blocks['1711261612064'] = {
  init: function() {
    this.jsonInit({
      "type": "1711261612064",
      "message0": "R-turn-00（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711261612064'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(68, 32, 90, 91, 132, 34, 190, 91, 129, 162, 105, 106, 167, 138, 137, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711261612064'] = function(block) {
  let code = "robot.leju_action('R-turn-00（2）')\n";
  return code;
}

Blockly.Blocks['1711261838846'] = {
  init: function() {
    this.jsonInit({
      "type": "1711261838846",
      "message0": "box-go-2min-q（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711261838846'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 90, 91, 48, 129, 88, 137, 190, 23, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711261838846'] = function(block) {
  let code = "robot.leju_action('box-go-2min-q（2）')\n";
  return code;
}

Blockly.Blocks['1711262014402'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262014402",
      "message0": "Box-Rturn1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262014402'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 102, 160, 60, 177, 95, 120, 170, 85, 101, 150, 133, 144, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(800)\n";
  return code;
}

Blockly.Python['1711262014402'] = function(block) {
  let code = "robot.leju_action('Box-Rturn1')\n";
  return code;
}

Blockly.Blocks['1711262044485'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262044485",
      "message0": "Box-1L",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262044485'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,14,20,65,85,95,85,35,20,20,20,65,55,55,55,35,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 82, 110, 75, 110, 87, 139, 190, 23, 119, 106, 154, 68, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711262044485'] = function(block) {
  let code = "robot.leju_action('Box-1L')\n";
  return code;
}

Blockly.Blocks['1711262124389'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262124389",
      "message0": "Rturn-q（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262124389'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 99, 160, 49, 190, 100, 120, 170, 85, 100, 161, 135, 148, 98, 120, 40, 100)\nMOTOwait()\nDelayMs(150)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711262124389'] = function(block) {
  let code = "robot.leju_action('Rturn-q（2）')\n";
  return code;
}

Blockly.Blocks['1711267493067'] = {
  init: function() {
    this.jsonInit({
      "type": "1711267493067",
      "message0": "sgt（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711267493067'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 1站立\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 2\nMOTOsetspeed(25)\nMOTOmove19(94, 79, 100, 85, 106, 79, 113, 80, 106, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 150, 100, 92, 152, 79, 156, 83, 100, 100, 100, 100, 135, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 100, 100, 81, 154, 78, 154, 84, 100, 100, 100, 99, 150, 158, 111, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 2右腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 100, 100, 106, 93, 55, 124, 112, 103, 95, 100, 115, 68, 73, 115, 111, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 100, 100, 105, 115, 100, 101, 110, 100, 50, 100, 115, 40, 150, 20, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 100, 100, 100, 65, 50, 101, 100, 100, 50, 100, 109, 49, 122, 44, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 55, 50, 101, 100, 100, 100, 100, 100, 40, 122, 45, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(300)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 90, 70, 10, 160, 90, 100, 190, 20, 95, 40, 122, 65, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 45, 20, 95, 100, 100, 190, 20, 95, 85, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 130, 90, 105, 100, 100, 190, 20, 95, 95, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 85, 110, 90, 105, 100, 100, 100, 20, 95, 102, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 3左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 150, 100, 85, 160, 78, 157, 93, 100, 100, 100, 100, 134, 155, 102, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 80, 160, 79, 156, 86, 100, 100, 100, 100, 145, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\n\n\n-- 15\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 180, 102, 79, 32, 137, 108, 100, 100, 20, 108, 121, 165, 70, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 100, 108, 70, 10, 148, 108, 100, 70, 100, 111, 101, 142, 72, 110, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,75,85,100,90,60,30,30,30,50,55,50,50,50,0,0,0)\n\n\n-- 4\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 105, 79, 32, 137, 108, 100, 70, 100, 107, 107, 160, 60, 112, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,50,60,60,60,60,30,30,30,50,60,60,60,60,0,0,0)\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 100, 79, 35, 130, 100, 100, 70, 100, 102, 107, 160, 65, 102, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 98, 79, 35, 130, 95, 100, 70, 100, 98, 107, 160, 65, 95, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 92, 79, 35, 130, 92, 100, 70, 100, 98, 121, 168, 63, 92, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 14\nMOTOsetspeed(20)\nMOTOmove19(80, 30, 100, 100, 95, 55, 123, 100, 120, 170, 100, 100, 105, 145, 77, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711267493067'] = function(block) {
  let code = "robot.leju_action('sgt（2）')\n";
  return code;
}

Blockly.Blocks['1711337549795'] = {
  init: function() {
    this.jsonInit({
      "type": "1711337549795",
      "message0": "box-down-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711337549795'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(60, 15, 190, 100, 93, 55, 130, 98, 132, 187, 10, 100, 107, 145, 70, 102, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 15, 190, 99, 90, 150, 38, 100, 132, 187, 10, 101, 111, 50, 163, 99, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(59, 14, 148, 99, 122, 150, 39, 100, 134, 188, 56, 101, 79, 50, 163, 99, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(72, 14, 147, 99, 122, 150, 39, 100, 130, 176, 57, 101, 79, 50, 163, 99, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(72, 14, 147, 99, 98, 150, 40, 100, 130, 176, 57, 100, 105, 50, 163, 99, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711337549795'] = function(block) {
  let code = "robot.leju_action('box-down-q')\n";
  return code;
}

Blockly.Blocks['1711337558773'] = {
  init: function() {
    this.jsonInit({
      "type": "1711337558773",
      "message0": "box-up00",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711337558773'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(64, 43, 93, 88, 148, 150, 69, 92, 120, 168, 115, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(76, 20, 158, 88, 148, 150, 69, 92, 118, 186, 44, 95, 43, 50, 116, 98, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(79, 34, 146, 65, 130, 145, 46, 67, 121, 168, 55, 131, 64, 50, 155, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 141, 69, 124, 139, 47, 72, 137, 190, 55, 128, 67, 52, 152, 126, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 180, 91, 114, 150, 48, 90, 137, 190, 23, 114, 84, 50, 151, 112, 120, 40, 99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 99, 107, 144, 75, 99, 120, 40, 99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711337558773'] = function(block) {
  let code = "robot.leju_action('box-up00')\n";
  return code;
}

Blockly.Blocks['1711342832136'] = {
  init: function() {
    this.jsonInit({
      "type": "1711342832136",
      "message0": "sgt（3）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711342832136'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 1站立\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 2\nMOTOsetspeed(25)\nMOTOmove19(94, 79, 100, 85, 106, 79, 113, 80, 106, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 150, 100, 92, 152, 79, 156, 83, 100, 100, 100, 100, 135, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 100, 100, 81, 154, 78, 154, 84, 100, 100, 100, 99, 150, 158, 111, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 2右腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 100, 100, 106, 93, 55, 124, 112, 103, 95, 100, 115, 68, 73, 115, 111, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,60,60,60,60,60,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 100, 100, 105, 115, 100, 101, 110, 100, 50, 100, 115, 40, 150, 20, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 100, 100, 100, 65, 50, 101, 100, 100, 50, 100, 109, 49, 122, 44, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 100, 55, 50, 101, 100, 100, 100, 100, 100, 40, 122, 45, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(300)\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 90, 70, 10, 160, 90, 100, 190, 20, 95, 40, 122, 65, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 45, 20, 95, 100, 100, 190, 20, 95, 85, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 85, 130, 90, 105, 100, 100, 190, 20, 95, 95, 135, 75, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,90,90,90,90,25,25,25,90,100,100,100,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 85, 110, 90, 105, 100, 100, 100, 20, 95, 102, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 3左腿上台阶\nMOTOsetspeed(15)\nMOTOmove19(97, 105, 100, 85, 132, 127, 85, 89, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\n\n\n-- 1\nMOTOsetspeed(35)\nMOTOmove19(100, 150, 100, 85, 160, 50, 180, 95, 100, 100, 100, 95, 85, 100, 99, 90, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(100, 150, 100, 85, 160, 78, 157, 93, 100, 100, 100, 100, 134, 155, 102, 110, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 100, 80, 160, 79, 156, 86, 100, 100, 100, 100, 145, 150, 99, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(100, 10, 180, 105, 160, 78, 135, 112, 100, 190, 20, 110, 130, 190, 40, 110, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 115, 65, 125, 112, 100, 190, 20, 115, 155, 180, 105, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 10, 180, 105, 105, 65, 125, 112, 100, 190, 20, 115, 70, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,90,100,100,100,90,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(100, 100, 180, 105, 98, 55, 124, 112, 100, 100, 20, 115, 90, 110, 95, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(200)\n\n\n-- 15\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 180, 102, 79, 32, 137, 108, 100, 100, 20, 108, 121, 165, 70, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(100, 100, 100, 108, 70, 10, 148, 108, 100, 70, 100, 111, 101, 142, 72, 110, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,75,85,100,90,60,30,30,30,50,55,50,50,50,0,0,0)\n\n\n-- 4\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 105, 79, 32, 137, 108, 100, 70, 100, 107, 107, 160, 60, 112, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(30,30,30,50,60,60,60,60,30,30,30,50,60,60,60,60,0,0,0)\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 100, 79, 35, 130, 100, 100, 70, 100, 102, 107, 160, 65, 102, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 98, 79, 35, 130, 95, 100, 70, 100, 98, 107, 160, 65, 95, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(100, 100, 100, 92, 79, 35, 130, 92, 100, 70, 100, 98, 121, 168, 63, 92, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 14\nMOTOsetspeed(20)\nMOTOmove19(80, 30, 100, 100, 95, 55, 123, 100, 120, 170, 100, 100, 105, 145, 77, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711342832136'] = function(block) {
  let code = "robot.leju_action('sgt（3）')\n";
  return code;
}

Blockly.Blocks['1711344124295'] = {
  init: function() {
    this.jsonInit({
      "type": "1711344124295",
      "message0": "左侧上高台7",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711344124295'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(79, 29, 99, 100, 93, 56, 125, 99, 119, 170, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(79, 29, 99, 100, 93, 56, 125, 99, 119, 170, 100, 98, 105, 138, 77, 90, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(79, 29, 99, 95, 129, 150, 57, 89, 119, 170, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 90, 139, 150, 65, 99, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 69, 138, 150, 63, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 91, 114, 190, 41, 91, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 61, 115, 90, 111, 60, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 61, 115, 90, 111, 60, 148, 190, 10, 94, 113, 187, 41, 94, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 51, 114, 94, 111, 60, 148, 190, 10, 94, 113, 187, 41, 94, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 51, 114, 94, 111, 60, 148, 190, 10, 101, 112, 186, 40, 106, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 51, 114, 94, 111, 60, 148, 190, 10, 88, 112, 186, 39, 95, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 90, 114, 150, 48, 92, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 90, 114, 150, 39, 107, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 122, 101, 97, 115, 150, 41, 111, 117, 105, 92, 102, 40, 50, 104, 108, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 122, 101, 97, 113, 150, 40, 104, 117, 105, 92, 102, 57, 54, 124, 118, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711344124295'] = function(block) {
  let code = "robot.leju_action('左侧上高台7')\n";
  return code;
}

Blockly.Blocks['1711345958911'] = {
  init: function() {
    this.jsonInit({
      "type": "1711345958911",
      "message0": "生n1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711345958911'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80, 30, 100, 107, 100, 56, 124, 111, 120, 170, 100, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(7)\nMOTOmove19(90, 88, 103, 100, 102, 56, 122, 113, 109, 39, 88, 99, 76, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(90, 88, 103, 100, 102, 56, 122, 113, 109, 39, 88, 179, 74, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(90, 160, 102, 100, 102, 55, 121, 93, 109, 101, 88, 179, 74, 50, 149, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(90, 160, 102, 100, 102, 55, 121, 93, 109, 101, 88, 169, 72, 50, 149, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(28)\nMOTOmove19(100, 75, 100, 50, 130, 138, 75, 80, 45, 33, 95, 150, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(21)\nMOTOmove19(100, 125, 100, 30, 130, 138, 75, 104, 45, 33, 95, 170, 70, 62, 125, 80, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(42)\nMOTOmove19(100, 140, 100, 20, 130, 138, 75, 110, 45, 43, 95, 180, 70, 62, 125, 80, 128, 71, 100)\nMOTOwait()\nDelayMs(900)\nMOTOsetspeed(14)\nMOTOmove19(100, 140, 100, 20, 130, 138, 75, 110, 99, 98, 101, 180, 116, 164, 66, 98, 128, 71, 100)\nMOTOwait()\nDelayMs(1000)\n";
  return code;
}

Blockly.Python['1711345958911'] = function(block) {
  let code = "robot.leju_action('生n1')\n";
  return code;
}

Blockly.Blocks['1711348020369'] = {
  init: function() {
    this.jsonInit({
      "type": "1711348020369",
      "message0": "下高台",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711348020369'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,25,70,70,70,70,70,25,25,25,70,70,70,70,70,0,0,0)\nMOTOsetspeed(53)\nMOTOmove19(101, 101, 101, 95, 120, 119, 85, 95, 135, 104, 99, 105, 80, 81, 115, 105, 128, 71, 100)\nMOTOwait()\nDelayMs(250)\nMOTOsetspeed(25)\nMOTOmove19(145, 155, 105, 90, 132, 138, 75, 108, 55, 45, 95, 105, 75, 85, 108, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(145, 155, 105, 78, 130, 138, 75, 110, 55, 45, 95, 110, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\n\n\n-- 4\nMOTOsetspeed(28)\nMOTOmove19(100, 75, 100, 50, 130, 138, 75, 80, 45, 33, 95, 150, 70, 62, 125, 111, 128, 71, 100)\nMOTOwait()\n\n\n-- 5\nMOTOsetspeed(28)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n\n\n-- 6\nMOTOsetspeed(35)\nMOTOmove19(80, 30, 100, 108, 93, 55, 124, 100, 120, 170, 100, 92, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711348020369'] = function(block) {
  let code = "robot.leju_action('下高台')\n";
  return code;
}

Blockly.Blocks['1711427133530'] = {
  init: function() {
    this.jsonInit({
      "type": "1711427133530",
      "message0": "上台阶侧边3",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711427133530'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 99, 106, 143, 75, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(93, 151, 102, 98, 160, 108, 138, 113, 109, 109, 88, 94, 88, 159, 59, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(101, 83, 98, 20, 137, 150, 62, 95, 119, 96, 100, 88, 105, 142, 76, 81, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 31, 104, 81, 117, 60, 119, 96, 100, 88, 104, 141, 77, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 148, 108, 186, 42, 139, 128, 71, 100)\nMOTOwait()\n\n\n-- 右脚幅度\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 51, 114, 94, 111, 60, 148, 190, 10, 88, 112, 186, 39, 95, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 90, 114, 150, 48, 92, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 90, 114, 150, 48, 92, 148, 190, 10, 107, 114, 187, 41, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 92, 111, 150, 37, 105, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 111, 116, 150, 48, 121, 148, 190, 10, 135, 115, 186, 41, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 111, 120, 150, 48, 121, 148, 190, 10, 135, 54, 185, 40, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 111, 120, 150, 48, 121, 148, 190, 10, 136, 41, 184, 10, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 110, 120, 150, 50, 123, 148, 190, 10, 135, 42, 183, 10, 136, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(81, 60, 98, 110, 120, 150, 50, 123, 148, 190, 10, 110, 42, 183, 10, 127, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(81, 60, 98, 110, 131, 150, 56, 104, 148, 190, 10, 112, 40, 167, 10, 103, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(81, 60, 98, 110, 110, 106, 65, 103, 148, 190, 10, 112, 40, 167, 10, 103, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(50)\n";
  return code;
}

Blockly.Python['1711427133530'] = function(block) {
  let code = "robot.leju_action('上台阶侧边3')\n";
  return code;
}

Blockly.Blocks['1711440016863'] = {
  init: function() {
    this.jsonInit({
      "type": "1711440016863",
      "message0": "抱块pro稳（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711440016863'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(150)\nMOTOmove19(78, 56, 100, 101, 113, 63, 128, 95, 115, 152, 101, 100, 86, 133, 74, 104, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(60)\nMOTOmove19(71, 46, 165, 53, 154, 150, 59, 62, 127, 163, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(73, 10, 164, 53, 154, 150, 59, 62, 130, 190, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(73, 10, 164, 100, 93, 55, 124, 100, 130, 190, 37, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711440016863'] = function(block) {
  let code = "robot.leju_action('抱块pro稳（2）')\n";
  return code;
}

Blockly.Blocks['1711440056030'] = {
  init: function() {
    this.jsonInit({
      "type": "1711440056030",
      "message0": "抱块3",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711440056030'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(130)\nMOTOmove19(80, 30, 145, 100, 93, 55, 124, 100, 119, 173, 51, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 145, 92, 107, 150, 38, 100, 119, 173, 51, 101, 69, 50, 145, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(80, 30, 160, 68, 125, 150, 44, 68, 119, 173, 51, 128, 68, 50, 157, 126, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(42, 38, 173, 45, 151, 150, 46, 62, 155, 178, 35, 145, 48, 50, 155, 138, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(42, 38, 173, 59, 150, 125, 97, 67, 155, 178, 35, 118, 47, 80, 93, 127, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(32)\nMOTOmove19(42, 38, 173, 96, 113, 63, 128, 95, 155, 178, 35, 102, 86, 133, 74, 104, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711440056030'] = function(block) {
  let code = "robot.leju_action('抱块3')\n";
  return code;
}

Blockly.Blocks['1711440985897'] = {
  init: function() {
    this.jsonInit({
      "type": "1711440985897",
      "message0": "box_up_x",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711440985897'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(150)\nMOTOmove19(78, 56, 100, 101, 113, 63, 128, 95, 115, 152, 101, 100, 86, 133, 74, 104, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 46, 165, 53, 154, 150, 59, 62, 127, 163, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(73, 10, 164, 53, 154, 150, 59, 62, 130, 190, 37, 140, 40, 50, 137, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 164, 100, 93, 55, 124, 100, 138, 190, 37, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711440985897'] = function(block) {
  let code = "robot.leju_action('box_up_x')\n";
  return code;
}

Blockly.Blocks['1713948389814'] = {
  init: function() {
    this.jsonInit({
      "type": "1713948389814",
      "message0": "上1642",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1713948389814'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 99, 106, 143, 75, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(93, 151, 102, 98, 160, 108, 138, 113, 109, 109, 88, 94, 88, 159, 59, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 21, 112, 82, 121, 60, 119, 96, 100, 88, 104, 141, 77, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 98, 106, 143, 76, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 61, 115, 90, 111, 60, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 83, 98, 71, 139, 150, 78, 75, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(100, 68, 96, 73, 136, 150, 76, 77, 119, 96, 100, 123, 114, 186, 41, 120, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 92, 111, 150, 37, 105, 148, 190, 10, 107, 115, 186, 42, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 111, 116, 150, 48, 121, 148, 190, 10, 135, 115, 186, 41, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81, 60, 98, 111, 100, 150, 48, 121, 148, 190, 10, 165, 90, 50, 149, 140, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(81, 60, 98, 112, 84, 61, 114, 115, 148, 190, 10, 169, 88, 50, 163, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(93, 79, 98, 109, 106, 57, 126, 111, 148, 190, 10, 113, 40, 173, 10, 117, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(52, 18, 190, 103, 51, 10, 113, 98, 148, 190, 10, 109, 44, 125, 43, 105, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(52, 18, 190, 106, 41, 11, 106, 99, 148, 190, 10, 104, 40, 129, 33, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(44, 21, 190, 99, 84, 41, 134, 97, 148, 190, 10, 96, 40, 143, 48, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(44, 21, 190, 98, 87, 40, 156, 98, 148, 190, 10, 96, 40, 143, 48, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(44, 21, 190, 98, 87, 40, 156, 98, 148, 190, 10, 93, 40, 142, 47, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(44, 21, 190, 97, 80, 66, 155, 100, 148, 190, 10, 104, 66, 140, 62, 92, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(44, 21, 190, 100, 94, 150, 37, 99, 148, 190, 10, 100, 93, 162, 53, 89, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1713948389814'] = function(block) {
  let code = "robot.leju_action('上1642')\n";
  return code;
}

Blockly.Blocks['1719126545343'] = {
  init: function() {
    this.jsonInit({
      "type": "1719126545343",
      "message0": "159",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719126545343'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(100,100,100,65,100,100,100,65,100,100,100,65,100,100,100,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(78, 16, 190, 98, 105, 149, 47, 100, 110, 190, 15, 100, 98, 50, 157, 98, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(78, 16, 190, 98, 143, 148, 46, 100, 110, 190, 15, 100, 59, 51, 157, 98, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(78, 16, 190, 97, 137, 85, 87, 99, 110, 190, 15, 98, 66, 116, 114, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(78, 40, 173, 100, 132, 101, 150, 99, 109, 166, 26, 100, 65, 94, 51, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(78, 40, 190, 99, 40, 117, 49, 99, 109, 166, 15, 100, 162, 80, 152, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(77, 39, 144, 99, 40, 117, 49, 99, 108, 165, 55, 100, 162, 80, 152, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(77, 39, 144, 100, 38, 46, 41, 97, 108, 165, 55, 99, 162, 152, 160, 97, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58, 50, 177, 77, 116, 91, 45, 116, 130, 179, 20, 141, 72, 121, 140, 118, 128, 71, 100)\nMOTOwait()\n\n\n-- 23\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 54, 148, 116, 62, 83, 104, 176, 10, 124, 51, 70, 146, 106, 128, 71, 100)\nMOTOwait()\n\n\n-- 222\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 55, 148, 118, 49, 82, 104, 184, 17, 134, 51, 81, 145, 116, 128, 71, 100)\nMOTOwait()\n\n\n-- 23\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 54, 148, 116, 62, 83, 104, 176, 10, 124, 51, 70, 146, 106, 128, 71, 100)\nMOTOwait()\n\n\n-- 222\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 55, 148, 118, 49, 82, 104, 184, 17, 134, 51, 81, 145, 116, 128, 71, 100)\nMOTOwait()\n\n\n-- 23\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 54, 148, 116, 62, 83, 104, 176, 10, 124, 51, 70, 146, 106, 128, 71, 100)\nMOTOwait()\n\n\n-- 222\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 55, 148, 118, 49, 82, 104, 184, 17, 134, 51, 81, 145, 116, 128, 71, 100)\nMOTOwait()\n\n\n-- 23\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 54, 148, 116, 62, 83, 104, 176, 10, 124, 51, 70, 146, 106, 128, 71, 100)\nMOTOwait()\n\n\n-- 222\nMOTOsetspeed(30)\nMOTOmove19(84, 38, 190, 55, 148, 118, 49, 82, 104, 184, 17, 134, 51, 81, 145, 116, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(85, 12, 172, 62, 160, 146, 47, 75, 119, 189, 31, 139, 43, 54, 154, 123, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(54, 47, 190, 70, 126, 145, 53, 68, 150, 147, 19, 138, 74, 60, 147, 135, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(54, 47, 190, 79, 113, 140, 50, 78, 150, 147, 19, 126, 72, 60, 135, 125, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(80, 30, 113, 100, 125, 140, 62, 100, 120, 170, 87, 100, 75, 60, 138, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(40)\nMOTOmove19(80, 30, 113, 104, 127, 133, 71, 100, 120, 170, 87, 103, 70, 67, 128, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80, 30, 99, 100, 92, 55, 124, 99, 119, 170, 99, 100, 107, 144, 75, 99, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1719126545343'] = function(block) {
  let code = "robot.leju_action('159')\n";
  return code;
}

Blockly.Blocks['1719127555289'] = {
  init: function() {
    this.jsonInit({
      "type": "1719127555289",
      "message0": "66cd7afb1ae2c1cf7fe4040b22085712_6337a0d6a8e1d87f89fdb394339a81de_8",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719127555289'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(60,60,60,30,60,60,60,30,60,60,60,30,60,60,60,30,0,0,0)\n\n\n-- 1站立\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(25)\nMOTOmove19(94, 79, 100, 85, 106, 79, 113, 80, 106, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOrigid16(25,25,25,60,60,60,60,60,25,25,25,90,90,90,90,90,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(97, 105, 100, 85, 131, 150, 63, 88, 103, 100, 100, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 10, 178, 85, 54, 75, 172, 89, 102, 189, 22, 94, 107, 145, 76, 88, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(101, 10, 178, 86, 63, 77, 138, 88, 102, 189, 22, 90, 53, 50, 134, 84, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(65, 36, 178, 91, 160, 60, 126, 106, 101, 188, 22, 92, 40, 50, 160, 94, 128, 71, 100)\nMOTOwait()\nDelayMs(70)\nMOTOsetspeed(30)\nMOTOmove19(70, 18, 178, 83, 160, 150, 55, 89, 101, 188, 22, 112, 57, 50, 159, 108, 128, 71, 100)\nMOTOwait()\nDelayMs(30)\nMOTOrigid16(70,18,178,40,40,40,40,40,101,188,22,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(70, 18, 178, 70, 126, 145, 53, 68, 101, 188, 22, 138, 74, 60, 147, 135, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70, 18, 178, 100, 125, 140, 62, 100, 101, 188, 22, 100, 75, 60, 138, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 113, 102, 128, 104, 97, 100, 120, 170, 87, 102, 74, 91, 104, 100, 128, 71, 100)\nMOTOwait()\n\n\n-- 站立\nMOTOsetspeed(30)\nMOTOmove19(80, 37, 100, 108, 93, 55, 124, 100, 120, 170, 100, 92, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1719127555289'] = function(block) {
  let code = "robot.leju_action('66cd7afb1ae2c1cf7fe4040b22085712_6337a0d6a8e1d87f89fdb394339a81de_8')\n";
  return code;
}

Blockly.Blocks['1747818499673'] = {
  init: function() {
    this.jsonInit({
      "type": "1747818499673",
      "message0": "bao1kuaiquanzou",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1747818499673'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(64, 10, 180, 90, 98, 47, 133, 86, 137, 190, 23, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(8)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1747818499673'] = function(block) {
  let code = "robot.leju_action('bao1kuaiquanzou')\n";
  return code;
}

Blockly.Blocks['1749217432407'] = {
  init: function() {
    this.jsonInit({
      "type": "1749217432407",
      "message0": "box_double_up_x",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749217432407'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(71, 72, 177, 62, 156, 150, 55, 68, 114, 141, 25, 136, 40, 50, 144, 131, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(71, 72, 177, 38, 156, 140, 46, 61, 114, 141, 25, 158, 42, 58, 155, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(91, 13, 177, 38, 156, 140, 46, 61, 106, 190, 19, 158, 42, 58, 155, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(91, 13, 177, 54, 143, 150, 68, 60, 106, 190, 19, 144, 41, 50, 121, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(67, 26, 190, 100, 93, 55, 124, 100, 129, 176, 10, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1749217432407'] = function(block) {
  let code = "robot.leju_action('box_double_up_x')\n";
  return code;
}

Blockly.Blocks['1749217450613'] = {
  init: function() {
    this.jsonInit({
      "type": "1749217450613",
      "message0": "box_doubleup_x1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749217450613'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(20)\nMOTOmove19(71, 72, 177, 62, 156, 150, 55, 68, 114, 141, 25, 136, 40, 50, 144, 131, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(71, 72, 177, 38, 156, 140, 46, 61, 114, 141, 25, 158, 42, 58, 155, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(91, 13, 177, 38, 156, 140, 46, 61, 106, 190, 19, 158, 42, 58, 155, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(91, 13, 177, 54, 143, 150, 68, 60, 106, 190, 19, 144, 41, 50, 121, 140, 128, 71, 99)\nMOTOwait()\nMOTOsetspeed(18)\nMOTOmove19(66, 26, 190, 100, 93, 55, 124, 100, 130, 176, 10, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1749217450613'] = function(block) {
  let code = "robot.leju_action('box_doubleup_x1')\n";
  return code;
}

