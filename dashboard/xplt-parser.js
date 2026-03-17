// xplt-parser.js - Server-side component for parsing FEBio .xplt files
const fs = require('fs');
const path = require('path');

class XPLTParser {
    parseXPLT(filePath) {
        return new Promise((resolve, reject) => {
            try {
                const buffer = fs.readFileSync(filePath);
                const data = this.parseBinaryXPLT(buffer);
                resolve(data);
            } catch (error) {
                reject(error);
            }
        });
    }

    parseBinaryXPLT(buffer) {
        // FEBio .xplt file structure parser
        const dataView = new DataView(buffer);
        let offset = 0;
        
        // Read header
        const magic = this.readString(buffer, offset, 6);
        offset += 6;
        
        if (magic !== "FEBIOX") {
            throw new Error("Invalid FEBio .xplt file");
        }
        
        const version = dataView.getFloat32(offset, true);
        offset += 4;
        
        // Read mesh information
        const nodes = dataView.getUint32(offset, true);
        offset += 4;
        
        const elements = dataView.getUint32(offset, true);
        offset += 4;
        
        // Read node coordinates
        const vertices = [];
        for (let i = 0; i < nodes; i++) {
            const x = dataView.getFloat32(offset, true);
            offset += 4;
            const y = dataView.getFloat32(offset, true);
            offset += 4;
            const z = dataView.getFloat32(offset, true);
            offset += 4;
            vertices.push([x, y, z]);
        }
        
        // Read elements (faces/tetrahedra)
        const faces = [];
        for (let i = 0; i < elements; i++) {
            const elementType = dataView.getUint32(offset, true);
            offset += 4;
            const nodeCount = dataView.getUint32(offset, true);
            offset += 4;
            
            const elementNodes = [];
            for (let j = 0; j < nodeCount; j++) {
                elementNodes.push(dataView.getUint32(offset, true));
                offset += 4;
            }
            
            // Convert to triangular faces for visualization
            if (nodeCount === 4) { // Tetrahedron
                faces.push([elementNodes[0], elementNodes[1], elementNodes[2]]);
                faces.push([elementNodes[0], elementNodes[2], elementNodes[3]]);
                faces.push([elementNodes[0], elementNodes[3], elementNodes[1]]);
                faces.push([elementNodes[1], elementNodes[3], elementNodes[2]]);
            } else if (nodeCount === 3) { // Triangle
                faces.push(elementNodes);
            }
        }
        
        // Read displacement data
        const displacements = [];
        const timeSteps = dataView.getUint32(offset, true);
        offset += 4;
        
        for (let t = 0; t < timeSteps; t++) {
            const time = dataView.getFloat32(offset, true);
            offset += 4;
            
            const stepDisplacements = [];
            for (let i = 0; i < nodes; i++) {
                const dx = dataView.getFloat32(offset, true);
                offset += 4;
                const dy = dataView.getFloat32(offset, true);
                offset += 4;
                const dz = dataView.getFloat32(offset, true);
                offset += 4;
                stepDisplacements.push([dx, dy, dz]);
            }
            displacements.push({
                time: time,
                displacements: stepDisplacements
            });
        }
        
        return {
            vertices: vertices,
            faces: faces,
            displacements: displacements,
            metadata: {
                nodes: nodes,
                elements: elements,
                timeSteps: timeSteps
            }
        };
    }

    readString(buffer, offset, length) {
        let result = '';
        for (let i = 0; i < length; i++) {
            result += String.fromCharCode(buffer[offset + i]);
        }
        return result;
    }
}

module.exports = XPLTParser;                                   