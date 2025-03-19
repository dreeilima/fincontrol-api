/*
  Warnings:

  - You are about to alter the column `amount` on the `transactions` table. The data in that column could be lost. The data in that column will be cast from `Decimal` to `Decimal(10,2)`.

*/
-- AlterTable
ALTER TABLE "categories" ADD COLUMN     "color" TEXT,
ADD COLUMN     "icon" TEXT;

-- AlterTable
ALTER TABLE "transactions" ALTER COLUMN "amount" SET DATA TYPE DECIMAL(10,2);

-- CreateIndex
CREATE INDEX "transactions_user_id_date_idx" ON "transactions"("user_id", "date");

-- CreateIndex
CREATE INDEX "transactions_category_idx" ON "transactions"("category");
