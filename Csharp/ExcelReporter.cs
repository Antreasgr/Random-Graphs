namespace ExcelReporter
{
    using System;
    using System.Collections.Generic;
    using System.Reflection;
    using DocumentFormat.OpenXml;
    using DocumentFormat.OpenXml.Packaging;
    using DocumentFormat.OpenXml.Spreadsheet;
    using DocumentFormat.OpenXml.Validation;

    public class ExcelReporter
    {
        public static void CreateSpreadsheetWorkbook(string filename, List<Statistics.Stats> stats)
        {
            // Create a spreadsheet document by supplying the filepath.
            // By default, AutoSave = true, Editable = true, and Type = xlsx.
            var spreadsheetDocument = SpreadsheetDocument.
                Create(filename + ".xlsx", SpreadsheetDocumentType.Workbook);

            // Add a WorkbookPart to the document.
            var workbookpart = spreadsheetDocument.AddWorkbookPart();
            workbookpart.Workbook = new Workbook();

            // Add a WorksheetPart to the WorkbookPart.
            var worksheetPart = workbookpart.AddNewPart<WorksheetPart>();
            var sheetData = new SheetData();
            worksheetPart.Worksheet = new Worksheet(sheetData);

            // Add Sheets to the Workbook.
            var sheets = spreadsheetDocument.WorkbookPart.Workbook.
                AppendChild<Sheets>(new Sheets());

            // Append a new worksheet and associate it with the workbook.
            var sheet = new Sheet()
            {
                Id = spreadsheetDocument.WorkbookPart.
                GetIdOfPart(worksheetPart),
                SheetId = 1,
                Name = filename
            };
            sheets.Append(sheet);

            var row = new Row();
            row.AppendChild(new Cell()
            {
                DataType = CellValues.String,
                CellValue = new CellValue(stats[0].Parameters["Algorithm"]),
            });
            sheetData.AppendChild(row);

            row = new Row();
            var row2 = new Row();

            // Write header row 2,3
            foreach (var key in stats[0].Parameters.Keys)
            {
                if (key != "Algorithm")
                {
                    row.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(key)
                    });
                    row2.AppendChild(new Cell());
                }
            }

            foreach (var key in stats[0].Output.Keys)
            {
                for (var i = 0; i < stats[0].Output[key].Count; i++)
                {
                    row.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? key : "")
                    });
                    row2.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? "mean" : "std")
                    });
                }
            }

            foreach (var key in stats[0].Times.Keys)
            {
                for (var i = 0; i < stats[0].Times[key].Count; i++)
                {
                    row.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? key : "")
                    });
                    row2.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? "mean" : "std")
                    });
                }
            }

            var properties = stats[0].CliqueTrees[0].GetType().GetProperties();
            foreach (var prop in properties)
            {
                for (var i = 0; i < stats[0].CliqueTrees.Count; i++)
                {
                    row.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? prop.Name : "")
                    });
                    row2.AppendChild(new Cell()
                    {
                        DataType = CellValues.String,
                        CellValue = new CellValue(i == 0 ? "mean" : "std")
                    });
                }
            }

            sheetData.AppendChild(row);
            sheetData.AppendChild(row2);

            // now write data
            var index = 0;
            foreach (var s in stats)
            {
                row = new Row();
                foreach (var item in s.Parameters)
                {
                    if (item.Key != "Algorithm")
                    {
                        row.AppendChild(new Cell()
                        {
                            DataType = CellValues.Number,
                            CellValue = new CellValue(Convert.ToString(item.Value, System.Globalization.CultureInfo.InvariantCulture))
                        });
                    }
                }

                foreach (var item in s.Output)
                {
                    for (var i = 0; i < item.Value.Count; i++)
                    {
                        row.AppendChild(new Cell()
                        {
                            DataType = CellValues.Number,
                            CellValue = new CellValue(Convert.ToString(item.Value[i], System.Globalization.CultureInfo.InvariantCulture))
                        });
                    }
                }

                foreach (var item in s.Times)
                {
                    for (var i = 0; i < item.Value.Count; i++)
                    {
                        row.AppendChild(new Cell()
                        {
                            DataType = CellValues.Number,
                            CellValue = new CellValue(Convert.ToString(item.Value[i], System.Globalization.CultureInfo.InvariantCulture))
                        });
                    }
                }

                foreach (var prop in properties)
                {
                    for (var i = 0; i < s.CliqueTrees.Count; i++)
                    {
                        var v = prop.GetValue(s.CliqueTrees[i]);
                        var isNumber = v is int || v is double;
                        row.AppendChild(new Cell()
                        {
                            DataType = isNumber ? CellValues.Number : CellValues.String,
                            CellValue = new CellValue(Convert.ToString(v, System.Globalization.CultureInfo.InvariantCulture))
                        });
                    }
                }

                sheetData.AppendChild(row);
                index++;
            }

            workbookpart.Workbook.Save();

            OpenXmlValidator validator = new OpenXmlValidator();
            var errors = validator.Validate(spreadsheetDocument);
            foreach (ValidationErrorInfo error in errors)
            {
                Console.Write(error.Description);
            }

            // Close the document.
            spreadsheetDocument.Close();
        }
    }
}