using System;
using System.Collections.Generic;
using System.Linq;
using INCR;
using MVA;
using ExcelReporter;

namespace Main
{
    public static class MainClass
    {
        static void Main(string[] args)
        {
            var shetStats = new SHET.SHET().RunSHET(3);
            Console.WriteLine("Done...");
            Console.WriteLine("Writing excel report...");
            ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("SHET", shetStats);
            Console.WriteLine("Done");

            var mvaStats = new MVAMain().RunMVA(3);
            Console.WriteLine("Done...");
            Console.WriteLine("Writing excel report...");
            ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("MVA", mvaStats);
            Console.WriteLine("Done");

            var incrStats = new INCRMain().RunINCR(10, 0);
            Console.WriteLine("Done...");
            Console.WriteLine("Writing excel report...");
            ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("INCR", incrStats);
            Console.WriteLine("Done");
        }
    }
}
