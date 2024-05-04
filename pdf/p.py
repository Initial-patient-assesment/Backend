from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib import styles
import json
from reportlab.lib import colors

def addTitle(doc,title,above,under,align=TA_LEFT):
	doc.append(Spacer(1,above))
	doc.append(Paragraph(title,ParagraphStyle(fontName="Helvetica",name='None', fontSize=32, alignment = align)))
	doc.append(Spacer(1,under))
	return doc
	
def addParagraphs(doc, parts):
	for part in parts:
		doc.append(Paragraph(part, ParagraphStyle(fontName="Helvetica",name='None', fontSize=14, bulletText='•',bulletFontSize = 14)))
		
		doc.append(Spacer(1,10))
	doc.append(Paragraph('__________________________________________________________________________________________________'))
	return doc
  
def addConv1(conv):
	data = []
	data.append([ Paragraph("How can I help you?", ParagraphStyle(fontName="Helvetica",name='None', fontSize=12, alignment=TA_CENTER)), Paragraph(conv[0]["content"], ParagraphStyle(fontName="Helvetica",name='None', fontSize=12, alignment=TA_CENTER))])
	for k, part in enumerate(conv[1:]):
		if part['role'] == 'assistant':
			a = Paragraph(conv[k+1]["content"], ParagraphStyle(fontName="Helvetica",name='None', fontSize=12, alignment=TA_CENTER))	
			try:
				u = Paragraph(conv[k+2]["content"], ParagraphStyle(fontName="Helvetica",name='None', fontSize=12, alignment=TA_CENTER, ))
				data.append([a,u])
			except: pass
	return data
	
def create_rep(json_data):
	
	try:
		conv = json_data[0]['convo']
		diags = json.loads(json_data[1])['potential_diagnosis']
		syms = json.loads(json_data[1])['patient_symptoms']
	except: pass

	styles = getSampleStyleSheet()
	document = []
	document.append(Image('logo.jpg', 1.6*inch, 1.33*inch))
	document = addTitle(document,'Symtoms',10,40)
	try:
		document = addParagraphs(document, syms)
		document = addTitle(document,'Potential Diagnoses',10,40)
		document = addParagraphs(document, diags)
		document = addTitle(document,'Conversation with bot',10,40,TA_CENTER)
		d = addConv1(conv)
	except: pass
	data = [
	    ['Assistent', 'Patient'],
	]
	try:
		for el in d:
			data.append(el)
	except: pass
	table = Table(data)

	style = TableStyle([
	    ('BACKGROUND', (0,0), (3,0), colors.black),
	    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), # The negative one means "go to the last element"
	    
	    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
	    
	    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
	    ('FONTSIZE', (0,0), (-1,0), 14),
	    
	    ('BOTTOMPADDING', (0,0), (-1,0), 12), # 12 = 12 pixels
	  
	    ('BACKGROUND', (0,1), (-1,-1), colors.beige), # Background for the rest of the table (excluding the title row)
	    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
	])
	table.setStyle(style)
	document.append(table)
	return document
